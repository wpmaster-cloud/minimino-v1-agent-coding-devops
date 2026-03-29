# ClickUp

Manage tasks, lists, and spaces in ClickUp using the Python CLI tool.

## Usage

All commands require `CLICKUP_API_TOKEN` to be set in the environment. Use `run_command` to execute.

| Command | Purpose |
|------|---------|
| `python3 scripts/clickup_tool.py get_teams` | List available teams (Workspaces) |
| `python3 scripts/clickup_tool.py get_spaces TEAM_ID` | List spaces in a team |
| `python3 scripts/clickup_tool.py get_folders SPACE_ID` | List folders in a space |
| `python3 scripts/clickup_tool.py get_lists FOLDER_ID` | List lists in a folder |
| `python3 scripts/clickup_tool.py get_tasks --list_id LIST_ID` | List tasks in a specific list |
| `python3 scripts/clickup_tool.py get_tasks --team_id TEAM_ID` | List all tasks in a team |
| `python3 scripts/clickup_tool.py create_task LIST_ID "Name" --description "..." --priority 1` | Create a new task |

## Workflow

### Finding the right location
1. **Get Team ID**: Use `get_teams`.
2. **Get Space ID**: Use `get_spaces TEAM_ID`.
3. **Get Folder/List**: Drill down via `get_folders` and `get_lists` until you have a `LIST_ID`.

### Managing Tasks
- **List existing**: Use `get_tasks --list_id LIST_ID`.
- **Create**: Use `create_task LIST_ID "Name"` with optional flags.

## Guardrails

- For large workspaces, drill down by team -> space -> folder -> list instead of searching everything.
- Status and Priority values should match ClickUp's allowed values for the specific list (use `get_tasks` of an existing task to see example status names).
