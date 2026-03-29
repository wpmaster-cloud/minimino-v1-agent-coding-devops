---
name: multi_agent_coordination
description: "Decompose a mission into parallel subtasks and coordinate multiple agents. Use when work can be parallelized, tasks are independent, or persistent worker agents are needed."
---

# Multi-Agent Coordination skill

Use this skill when the mission requires parallel work, dividing a task across multiple agents, or orchestrating persistent worker agents.

## CRITICAL: spawn_tasks vs worker agents

| | `spawn_tasks` | Worker Agents |
|---|---|---|
| **What it is** | Ephemeral subprocesses that run and exit | Persistent background processes sharing the same binary and workspace |
| **Lifecycle** | Spawned on demand, die when done (5-min timeout) | Keep running, processing missions from Redis queue one at a time |
| **Created by** | `spawn_tasks` tool call | Launching `minimino` binary in background with a different `AGENT_NAME` |
| **Missions sent via** | Automatic — included in the tool call | `scripts/workers.sh send <name> "mission"` |
| **Status checked via** | Collected automatically from stdout | `scripts/workers.sh status <name>` |

**NEVER use `spawn_tasks` when the user asks for "worker agents".**
For full worker agent instructions, read `skills/worker_agents/SKILL.md`.

## When to use which

| Scenario | Use |
|----------|-----|
| User says "create worker agents" or "spawn persistent agents" | Worker agents (see worker_agents skill) |
| 3-5 independent short subtasks, results needed now | `spawn_tasks` |
| Long-running, recurring, or persistent agent work | Worker agents |
| Quick parallel data gathering or processing | `spawn_tasks` |

## spawn_tasks workflow (EPHEMERAL)

1. **Decompose** — Break the mission into independent, self-contained tasks. Each task must include ALL context since subagents have no memory of your conversation.
2. **Spawn** — Use the `spawn_tasks` tool:
   ```
   spawn_tasks with tasks:
   [
     {"name": "task-1", "mission": "Scrape https://example.com and extract all article titles. Return them as a JSON array."},
     {"name": "task-2", "mission": "Scrape https://other.com and extract all article titles. Return them as a JSON array."}
   ]
   ```
3. **Collect** — Results come back as `[TASK_RESULT task-1]` blocks with VERIFIED/STUCK status.
4. **Aggregate** — Combine results into the final output.

### Writing good task missions
- Include the full URL, not "the same URL as before"
- Include the exact output format expected
- Include specific tool instructions if the task needs a particular script
- Keep each task focused on one thing — smaller tasks succeed more often

## Worker agents workflow (PERSISTENT)

Workers are **persistent background processes** running the same `minimino` binary. They share the same workspace, skills, scripts, and tools. Each worker has its own `AGENT_NAME` and listens on a Redis mission queue.

### Creating a worker agent

```bash
AGENT_NAME=<worker-name> PARENT_AGENT="$AGENT_NAME" nohup minimino > /dev/null 2>&1 &
```

With custom prompt or description:
```bash
AGENT_NAME=researcher PARENT_AGENT="$AGENT_NAME" AGENT_DESCRIPTION="Research specialist" ADDITIONAL_PROMPT="Focus on accuracy and citations." nohup minimino > /dev/null 2>&1 &
```

### Managing workers

```bash
scripts/workers.sh list                   # list all registered workers + status
scripts/workers.sh status <name>          # check status (VERIFIED/STUCK/UNKNOWN)
scripts/workers.sh send <name> <mission>  # queue a mission
scripts/workers.sh messages <name> [n]    # last n conversation messages
scripts/workers.sh events <name> [n]      # last n event stream entries
scripts/workers.sh deregister <name>      # remove from registry
```

### Workflow
1. **List** existing workers: `scripts/workers.sh list`
2. **Create** if needed (launch minimino in background with new AGENT_NAME)
3. **Verify** registered: `scripts/workers.sh list`
4. **Send** mission: `scripts/workers.sh send <name> "fully self-contained mission text"`
5. **Poll** until done: `scripts/workers.sh status <name>`
6. **Inspect** if needed: `scripts/workers.sh messages <name> 30`

## Guardrails

- Max depth is 3 (default). Subagents cannot spawn beyond this.
- Each subagent (spawn_tasks) has a 5-minute timeout.
- Never assume subagents share your context — every task mission must be fully self-contained.
- Do not spawn more than 5 tasks at once without good reason.
- If a task comes back STUCK, read its output before retrying.
- For persistent workers: always poll `status` — never assume completion.
- **Always list** existing workers before creating new ones.
- Do NOT call `done` on your own mission until workers report `status=VERIFIED`.
