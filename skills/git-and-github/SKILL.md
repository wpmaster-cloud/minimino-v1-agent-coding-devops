# Git and GitHub

Manage version control with standard `git` and repository/PR workflows with the GitHub CLI (`gh`).

## Authentication

- **GitHub CLI (`gh`)**: Automatically authenticated via the `GITHUB_TOKEN` environment variable.
- **Git**: Configured with `GIT_USER_NAME` and `GIT_USER_EMAIL`. For remote operations, use the token-in-URL pattern:
  ```bash
  git remote set-url origin https://x-access-token:$GITHUB_TOKEN@github.com/owner/repo.git
  ```

## Common Operations

| Operation | Command |
|-----------|---------|
| Status | `git status` |
| Add & Commit | `git add -A && git commit -m "feat: description"` |
| Branching | `git checkout -b feature/name` |
| Push | `git push -u origin $(git rev-parse --abbrev-ref HEAD)` |
| Pull | `git pull origin main` |
| Log | `git log --oneline -n 10` |

## GitHub Workflows (`gh`)

| Category | Command |
|----------|---------|
| **Repo** | `gh repo create <name> --public` / `gh repo clone <owner>/<repo>` |
| **PR** | `gh pr create --title "Title" --body "Summary"` / `gh pr status` |
| **List** | `gh pr list` / `gh repo list` |
| **Issues** | `gh issue create --title "Title"` / `gh issue list` |

## Workflow Patterns

### 1. Feature Development
1. `git checkout -b feature/my-feature`
2. Make changes, `git add -A`, `git commit -m "..."`
3. `git push -u origin feature/my-feature`
4. `gh pr create --fill`

### 2. Searching
- `gh repo search "query"`
- `gh search issues "keyboard" --repo owner/repo`

## Guardrails

- **Branching**: Always work on a feature branch.
- **Secrets**: Never commit API keys or tokens.
- **Tools**: Use `gh` for GitHub-specific tasks (repos, PRs, issues) - it's safer and faster.
- **Verification**: Run `git status` before committing.
