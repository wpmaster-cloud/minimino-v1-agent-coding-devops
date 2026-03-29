---
name: workflow
description: "Create, save, and run reusable workflows with mechanical step-by-step execution. Use when asked to define a workflow, save a repeatable process, or execute a named workflow."
---

# Workflow skill

Use this skill when the mission is repeatable, needs predictable steps, or should be pre-built once and reused later.

## How workflows work

A workflow is a saved JSON document with ordered steps. When you call `run_workflow`, each step executes as an **isolated agent** — fresh conversation, step-specific context, optionally restricted tools. The Go code controls progression, not the LLM. Progress is tracked in Redis and survives crashes.

## Step properties

| Field | Required | Purpose |
|-------|----------|---------|
| `stepTitle` | yes | Short label for the step |
| `stepPrompt` | yes | The mission — what the agent should accomplish |
| `context` | no | Extra background text for this step |
| `skills` | no | Skill names to load (SKILL.md injected into system prompt) |
| `tools` | no | Restrict available tools (empty = all tools). `done` and `stuck` are always included. |
| `inputs` | no | Names of output variables from previous steps to inject into the prompt |
| `outputVar` | no | Capture this step's done summary under this name for later steps |

The workflow itself also has a `context` field for shared background injected into every step.

## Workflow

1. Check if a similar workflow exists: `list_workflows`, `read_workflow`
2. Save the workflow with `save_workflow`
3. Execute it with `run_workflow`

## Example

```json
{
  "name": "deploy-service",
  "description": "Build and deploy to k8s",
  "context": "Service: minimino. Image: fooksmedia/minimino:latest. Cluster: prod.",
  "steps": [
    {
      "stepTitle": "Build binary",
      "stepPrompt": "Cross-compile the Go binary: GOOS=linux GOARCH=arm64 go build -o minimino. Verify the binary exists.",
      "tools": ["run_command", "done", "stuck"],
      "outputVar": "build_result"
    },
    {
      "stepTitle": "Run tests",
      "stepPrompt": "Run go vet ./... and go build ./.... Both must pass with zero errors.",
      "tools": ["run_command", "verify", "stuck"]
    },
    {
      "stepTitle": "Deploy to k8s",
      "stepPrompt": "Apply the k8s manifest and wait for rollout to complete.",
      "skills": ["kubernetes"],
      "inputs": ["build_result"],
      "tools": ["run_command", "read_file", "verify", "stuck"]
    }
  ]
}
```

## Data flow between steps

- A step with `"outputVar": "build_result"` captures its done summary under that name.
- A later step with `"inputs": ["build_result"]` receives: `$build_result = <captured value>` in its prompt.
- Only explicitly declared inputs are passed — steps don't see each other's full conversations.

## Guardrails

- Keep workflows focused. One workflow = one repeatable job.
- Make `stepPrompt` self-contained. Each step runs in isolation with no conversation history from previous steps.
- If a step calls `stuck`, the entire workflow aborts. Design steps to be achievable.
- Use `tools` restriction for safety — a read-only step should only have `["run_command", "read_file", "done", "stuck"]`.
- Completed workflows restart from step 1 if run again. Failed workflows resume from the failed step.
- If a workflow changes, overwrite it with `save_workflow`.
