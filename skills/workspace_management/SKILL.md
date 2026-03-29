---
name: workspace_management
description: "Navigate and organize the workspace filesystem. Use when the mission requires reading, creating, modifying, or organizing files, scripts, and directories in the workspace."
---

# Workspace Management skill

Use this skill when your mission requires reading, creating, modifying, or organizing files and shell scripts in your workspace.

## Workspace Layout

Your working directory is an isolated workspace. All paths are relative to it:
- `files/` — your primary storage for generated data, reports, code, and outputs.
- `skills/<name>/` — skill folders with instructions (read-only).

## Session Management

Use the `clear_session` tool to clear agent state when needed.

### Clear default session
```json
{
  "name": "clear_session",
  "arguments": {
    "name": "AGENT_NAME"
  }
}
```

### Clear specific session
```json
{
  "name": "clear_session",
  "arguments": {
    "name": "AGENT_NAME",
    "session": "SESSION_ID"
  }
}
```

## Core Rules

1. **Relative paths only:** When using `read_file`, `write_file`, or `edit_file`, provide paths relative to the workspace root (e.g., `files/app.js` or `scripts/build.sh`).
2. **Organize outputs:** Put generated files in logical subdirectories inside `files/`. E.g., financial data in `files/financial_data/`, reports in `files/reports/`.
3. **Create directories first:** Use `run_command` with `mkdir -p files/<name>` before writing files to new directories.
4. **Script creation:** Use `write_file` for `scripts/name.sh`, then `run_command` with `chmod +x scripts/name.sh`.
5. **Inspect contents:** Use `run_command` with `ls -la files/` to review file listings.

## Python for file processing

Python3 is natively available. Use it for data processing tasks:
```
run_command: "python3 -c \"import os; [print(f) for f in os.listdir('files/')]\""
```

For large file operations, write a script:
```
write_file path: "files/process.py" content: "<python code>"
run_command: "python3 files/process.py"
```

## Guardrails

- Never execute destructive operations like `rm -rf files/` without certainty.
- Do not modify files in `skills/` or `.env` unless explicitly part of your mission.
- For large files, use shell commands like `head`, `tail`, or `grep` via `run_command` instead of `read_file`.
