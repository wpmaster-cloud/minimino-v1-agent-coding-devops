---
name: spawn_tasks
description: Instructions on how to spawn background worker tasks
---
# Spawning Background Tasks

You can launch background subagents to work on tasks in parallel or independently by invoking the Minimino binary directly via the `run_command` tool.

When you need to distribute work or kick off an async task, use this command format:

```bash
./minimino -mission "The detailed task you want the subagent to accomplish" &
```

## Important Rules:

1. **Include the `. /minimino` binary**: Always run the binary from the current workspace root.
2. **Use the `-mission` flag**: This is required for subagents.
3. **Background the process**: Always append `&` to the end of the command so that the task runs asynchronously in the background and does not block your execution.
4. **Be highly descriptive**: Subagents do not automatically inherit your full context. The `-mission` text must be comprehensive enough that a fresh model can understand exactly what needs to be done.

**Example:**
If you need to summarize 5 different log files, you can spawn 5 separate subagents in parallel:
```bash
./minimino -mission "Read api.log, summarize the top errors, and write the report to api_summary.md" &
./minimino -mission "Read auth.log, summarize the top errors, and write the report to auth_summary.md" &
... (run via run_command)
```
