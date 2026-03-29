---
name: worker_agents
description: "Create, manage, and send missions to persistent worker agents. Use when the mission involves creating new agents, delegating work to other agents, checking worker status, or reading worker output. NOT for ephemeral sub-tasks (use spawn_tasks for those)."
---

# Worker Agents

Use this skill when the mission requires creating persistent worker agents, dispatching work to them, checking their status, or reading their output.

## What are worker agents?

Worker agents are **persistent background processes** running the same `minimino` binary and sharing the same workspace, skills, and scripts. Each worker has its own `AGENT_NAME` and listens on a Redis mission queue for work.

**Worker agents vs spawn_tasks:**
- `spawn_tasks` — ephemeral subprocesses that run one mission and die (5-minute timeout)
- Worker agents — persistent processes that keep running, processing missions from their Redis queue one at a time

## Managing workers

Use the native worker tools for all operations:

### List all workers
Use the `list_workers` tool to see all active agents.

### Create a new worker
Use the `create_worker` tool with parameters `name` and `description`.

### Send a mission
Use the `send_mission` tool with parameters `name` and `mission`.

### Kill a worker
Use the `kill_worker` tool with parameter `name` to cleanly terminate it.

### Check worker status
Use the `worker_status` tool with parameter `name`.

### Read worker events/messages
Use the `worker_events` tool with parameter `name`.

## Workflow

1. **List** existing workers via `list_workers`.
2. **Create** a new worker if needed via `create_worker`.
3. **Verify** registration by listing again.
4. **Send** a mission via `send_mission`.
5. **Poll** status via `worker_status` until it returns `DONE` or `STUCK`.
6. **Inspect** results via `worker_events`.
7. **Kill** the worker when no longer needed using `kill_worker`.

## Guardrails

- Missions must be fully self-contained strings.
- Worker names must be unique.
- Always use the native tools rather than shell scripts for consistent state handling.
