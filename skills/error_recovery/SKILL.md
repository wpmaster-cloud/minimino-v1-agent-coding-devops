---
name: error_recovery
description: "Cross-cutting error handling guide. Apply when encountering repeated errors, network failures, rate limits (429), auth failures, empty responses, or oversized output."
---

# Error Recovery skill

Use this skill as a cross-cutting guide when encountering failures during any mission. It covers common failure patterns and how to handle them.

## Goal

Recover from errors efficiently — retry smartly, pivot when needed, and `stuck` decisively when recovery is impossible.

## Core rule

Same error twice on the same action → immediately `stuck`. Never retry a third time with the same approach.

## Common failure patterns

### Network / timeout errors
- **Symptom**: `curl: (28) Operation timed out`, connection refused, DNS resolution failed.
- **Recovery**: Wait 5 seconds, retry once. If still failing, the service is likely down — `stuck` with the error.
- **For web_scraper.sh**: Increase `--http-timeout=60`. If a page is slow, add `--wait=5000`.

### API rate limits (429)
- **Symptom**: HTTP 429, "rate limit exceeded", "too many requests".
- **Recovery**: Wait 10–15 seconds before retrying. Reduce batch size. For LinkedIn, reduce `limit` parameter.
- **Prevention**: Don't scrape/call the same API more than 10 times in rapid succession.

### Authentication failures
- **Symptom**: HTTP 401/403, "unauthorized", "forbidden", "invalid token".
- **Recovery**: Check that the required env var is set (`run_command: echo $VAR_NAME | head -c 5`). If empty, `stuck` with "missing credentials."
- **For LinkedIn MCP**: Try `linkedin_check_auth` with `force_reauth: true` once.

### Empty / unusable responses
- **Symptom**: Tool returns empty string, blank page, CAPTCHA, login wall.
- **Recovery**:
  - Web scraper: Try `--wait=5000`, or `--format=html` to see raw content. If it's a block page, try a different source.
  - MCP tools: Check that parameters match the expected format. Try a simpler query.
- **If content is behind a login wall**: Skip that source and note it was inaccessible. Do not attempt to log in unless the mission explicitly provides credentials.

### Command execution failures
- **Symptom**: `exit=1`, permission denied, command not found.
- **Recovery**:
  - Permission denied: `chmod +x` the script.
  - Command not found: Check the tool/script actually exists (`ls ./scripts/`).
  - Script error: Read the stderr output carefully — fix the root cause, not the symptom.

### MCP tool not available
- **Symptom**: Tool call returns error about unknown tool, or MCP server unreachable.
- **Recovery**: The MCP server may not be deployed. List available tools to see what's actually accessible. Use an alternative approach (e.g., web_scraper.sh instead of a specialized MCP).

### Large output truncation
- **Symptom**: Output is cut off at max output limit (8000 chars default).
- **Recovery**: Pipe through `head`, `tail`, or `grep` to get the specific part you need. Or redirect to a file and read specific sections.

## Decision tree

```
Error occurs
├── First time? → Analyze error, adjust approach, retry once
├── Second time (same error)? → stuck immediately
├── Different error? → It's a new problem — analyze and try once
└── Partial success? → Save what worked, retry only the failed part
```

## Guardrails

- Never silently ignore errors. Always check exit codes and tool responses.
- Never retry more than once with the same parameters.
- When pivoting, change something meaningful — different URL, different tool, different parameters. Not just the same call again.
- Log what failed and why in the `stuck` reason so the user can diagnose.
- If multiple independent steps fail, try the remaining steps before giving up — partial results are better than none.
