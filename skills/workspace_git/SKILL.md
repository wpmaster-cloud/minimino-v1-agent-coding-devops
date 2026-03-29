---
name: workspace_git
description: "Per-agent GitHub repo for version-controlled workspace. Repo is auto-created at startup — agent just needs to commit and push progress."
---

# Workspace Git

Your entire workspace is automatically backed by a GitHub repo: `wpmaster-cloud/minimino-v1-agent-{K8S_NAMESPACE}-{AGENT_NAME}`. It is set up at container startup — no manual init needed.

## During Your Mission

- Work inside the workspace as usual (`files/`, `scripts/`, etc.).
- Commit and push at meaningful checkpoints — not after every small change.
  ```bash
  git add -A && git commit -m "your message" && git push
  ```

## Commit Messages as Memory

Your git history is your journal. Write commit messages that your future self can use to understand what happened, what was decided, and why.

**Format:** `[category] what happened — why/context`

Categories: `data`, `research`, `code`, `config`, `fix`, `docs`, `experiment`

**Examples:**
- `[research] analyzed Q4 revenue trends — CFO requested focus on subscription churn`
- `[data] fetched 2024 sales data from API — 1,247 records, filtered to US region`
- `[code] built price prediction model — using linear regression, R²=0.87`
- `[fix] corrected date parsing — API returns ISO format not Unix timestamps`
- `[experiment] tested random forest vs gradient boosting — GBM wins by 3% accuracy`

**At mission start**, check your recent history for context:
```bash
git log --oneline -20
```

This helps you pick up where you left off and avoid repeating work.

## Guardrails

- Never commit secrets, API keys, or tokens.
- Never force-push. If push fails, pull first then retry.
- Always work on `main` unless the mission specifically requires branching.
