---
name: gh_issues
description: "Auto-fix GitHub issues by spawning parallel sub-agents that branch, implement fixes, and open PRs. Use when asked to autonomously fix, resolve, or triage GitHub issues."
---

# GitHub Issues skill

Use this skill when the mission requires automatically fixing GitHub issues by spawning parallel sub-agents that implement fixes, push branches, and open pull requests.

## Goal

Fetch open issues from a GitHub repository, spawn sub-agents to implement fixes and open PRs in parallel, then optionally handle PR review comments. Each sub-agent works on one issue independently.

## Prerequisites

- `GH_TOKEN` in `.env` with `repo` scope.
- The repository must be cloneable from the container (HTTPS token or SSH key).
- Maximum 8 issues per run (sub-agent concurrency limit).

## Phase 1 — Parse

Extract from the mission text:

- `owner/repo` — required
- `--label <label>` — filter issues by label (optional)
- `--limit <N>` — max issues to fetch, default 10
- `--state open|closed|all` — default `open`
- `--fork user/repo` — push branches to a fork; PRs target the source repo
- `--dry-run` — fetch and display only, no sub-agents
- `--reviews-only` — skip issue fixing, only handle open PR review comments
- `--notify-channel <telegram_channel_id>` — send Telegram summary when done

## Phase 2 — Fetch issues

```bash
curl -s \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page={limit}&labels={label}"
```

Filter out any item where the `pull_request` key exists — the Issues API also returns PRs.

Extract from each issue: `number`, `title`, `body`, `labels` (array of names), `html_url`.

## Phase 3 — Present and confirm

Display a Markdown table:

```
| #  | Title                        | Labels        |
|----|------------------------------|---------------|
| 42 | Fix null pointer in parser   | bug, critical |
| 37 | Add retry logic for API calls| enhancement   |
```

Ask the user: **"Process all, specific numbers (comma-separated), or cancel?"**

If `--dry-run`: display the table and stop — do not proceed to Phase 4.

## Phase 4 — Pre-flight checks

For each confirmed issue number N:

1. **Check for existing PR**:
   ```bash
   curl -s -H "Authorization: Bearer $GH_TOKEN" \
     "https://api.github.com/repos/{owner}/{repo}/pulls?head={owner}:fix/issue-{N}&state=open"
   ```
   If an open PR already exists, skip that issue and report it.

2. **Check claims** — Read memory key `gh-issues:claims:{owner}-{repo}`:
   - Parse the JSON. If issue N is present with a timestamp under 2 hours old, skip it: "Sub-agent has this issue in progress."
   - Drop expired entries (> 2 hours) and write the cleaned JSON back via `save_memory`.

3. **Record base branch**:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```

## Phase 5 — Spawn sub-agents

Before spawning, write the claimed issue numbers to memory. Use `save_memory` with key `gh-issues:claims:{owner}-{repo}` and a JSON object mapping each issue number to the current ISO timestamp.

Use `spawn_tasks` with one task per confirmed issue (up to 8 concurrent). Each task mission is fully self-contained:

```
You are a focused code-fix agent. Fix GitHub issue #{number} in {owner}/{repo} and open a PR.

REPO: {owner}/{repo}
PUSH REPO: {push_repo}
BASE BRANCH: {base_branch}
GH_TOKEN is available in the environment. Use it in all API calls:
  -H "Authorization: Bearer $GH_TOKEN"

ISSUE #{number}: {title}
BODY:
{body}

Follow these steps in order. Stop and report if any step fails.

1. CLONE
   git clone https://x-access-token:$GH_TOKEN@github.com/{push_repo}.git /tmp/repo-{number}
   cd /tmp/repo-{number}

2. BRANCH
   git checkout -b fix/issue-{number} {base_branch}

3. UNDERSTAND
   Read the issue. Search the codebase (grep/find) for relevant code.
   Rate your confidence 1-10. If < 7, stop and report: "Low confidence — {reason}."

4. IMPLEMENT
   Make the minimal focused fix. Follow existing code style. Do not change unrelated code.

5. TEST
   Detect and run the existing test suite (package.json scripts, Makefile, pytest, go test, etc.).
   If tests fail, attempt one fix. If they still fail, report the failure and continue.

6. COMMIT
   git add -A
   git commit -m "fix: {short_description}

Fixes {owner}/{repo}#{number}"

7. PUSH
   git remote set-url origin https://x-access-token:$GH_TOKEN@github.com/{push_repo}.git
   git push -u origin fix/issue-{number}

8. OPEN PR
   curl -s -X POST \
     -H "Authorization: Bearer $GH_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/repos/{owner}/{repo}/pulls \
     -d '{
       "title": "fix: {title}",
       "head": "{head_ref}",
       "base": "{base_branch}",
       "body": "## Summary\n\n{fix_description}\n\nFixes #{number}"
     }'
   Extract html_url from the response.

9. REPORT
   Return: PR URL, files changed, fix summary, any caveats or test failures.
```

For `head_ref`: use `fix/issue-{number}` in normal mode, `{fork_owner}:fix/issue-{number}` in fork mode.

If `--notify-channel` was provided, append a step 10 to each task mission:
```
10. NOTIFY
    run_command: ./scripts/telegram.sh message "✅ PR opened for #{number}: {title}\n{pr_url}"
```

Collect results. Present a summary table once all sub-agents complete:

```
| Issue | Status   | PR URL                          | Notes              |
|-------|----------|---------------------------------|--------------------|
| #42   | PR opened| https://github.com/.../pull/99  | 3 files changed    |
| #37   | Failed   | —                               | Tests failing      |
```

If `--notify-channel` was provided, send the final table summary:
```
./scripts/telegram.sh message "GitHub Issues Run Complete\n\n{summary}"
```

## Phase 6 — PR review handler (optional)

Run this phase when `--reviews-only` is set, or after Phase 5 completes.

1. **Fetch open fix PRs**:
   ```bash
   curl -s -H "Authorization: Bearer $GH_TOKEN" \
     "https://api.github.com/repos/{owner}/{repo}/pulls?state=open&per_page=100"
   ```
   Filter to PRs where `head.ref` starts with `fix/issue-`.

2. **Fetch review comments for each PR**:
   ```bash
   # Inline review comments
   curl -s -H "Authorization: Bearer $GH_TOKEN" \
     "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"

   # General PR discussion comments
   curl -s -H "Authorization: Bearer $GH_TOKEN" \
     "https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
   ```

3. **Filter actionable comments** — Keep comments that: request specific changes, say "please fix", "needs to", "should be", "will fail/break", or contain inline code suggestions. Skip: pure approvals, LGTM, bot auto-comments, already-addressed comments.

4. **Spawn fix sub-agents** via `spawn_tasks` — one per PR with unaddressed comments. Each sub-agent: checks out the branch, implements the requested changes, commits, pushes, and replies to each comment via the GitHub API:
   ```bash
   curl -s -X POST \
     -H "Authorization: Bearer $GH_TOKEN" \
     "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies" \
     -d '{"body": "Addressed in commit {short_sha} — {description}"}'
   ```

## Guardrails

- Verify `GH_TOKEN` before starting: `curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/user | jq .login`
- Sub-agents have a **5-minute timeout**. This skill works best for simple, well-scoped issues (single file or function). Complex multi-file refactors will likely timeout — warn the user upfront.
- Maximum 8 sub-agents per `spawn_tasks` call. For > 8 issues, batch across two runs.
- Always check for existing `fix/issue-{N}` PRs before spawning — avoid duplicate work.
- Use claim tracking (`save_memory` key `gh-issues:claims:{owner}-{repo}`) to prevent re-processing issues already in flight.
- Do not force-push. If a branch already exists on the remote, skip that issue.
- In fork mode: branches are pushed to `push_repo`, PRs are created on the source `owner/repo`. Set `head_ref` to `{fork_owner}:fix/issue-{N}`.
- If `--dry-run` is set, stop after Phase 3 — never spawn agents.
- If all issues are skipped (existing PRs or active claims), report "No eligible issues to process" and done.
