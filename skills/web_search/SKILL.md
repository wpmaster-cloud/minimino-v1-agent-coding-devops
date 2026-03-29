# Web Search skill

Use this skill to search the web for current information, news, or finding URLs via the Brave Search API.

## API Configuration

**Endpoint**: `https://api.search.brave.com/res/v1/web/search`  
**API Key**: `BSAF1ntdKw1-W42GzQYb8FNN93Zsd6u` (Hardcoded)

## Usage

Use `curl` with `jq` for formatted output. Always use `run_command`.

### Web Search (Text Output)

```bash
curl -s -G "https://api.search.brave.com/res/v1/web/search" \
  -H "X-Subscription-Token: BSAF1ntdKw1-W42GzQYb8FNN93Zsd6u" \
  --data-urlencode "q=YOUR_QUERY" \
  --data-urlencode "count=10" | jq -r '.web.results[] | "url: \(.url)\ntitle: \(.title)\nsnippet: \(.description // "")\n---"'
```

### Web Search (URLs Only)

```bash
curl -s -G "https://api.search.brave.com/res/v1/web/search" \
  -H "X-Subscription-Token: BSAF1ntdKw1-W42GzQYb8FNN93Zsd6u" \
  --data-urlencode "q=YOUR_QUERY" \
  --data-urlencode "count=10" | jq -r '.web.results[].url'
```

### News Search

```bash
curl -s -G "https://api.search.brave.com/res/v1/news/search" \
  -H "X-Subscription-Token: BSAF1ntdKw1-W42GzQYb8FNN93Zsd6u" \
  --data-urlencode "q=YOUR_QUERY" \
  --data-urlencode "count=5" | jq -r '.results[] | "url: \(.url)\ntitle: \(.title)\nsnippet: \(.description // "")\n---"'
```

## Options

- `count=N` — Number of results (max 20)
- `freshness=pd` — Past day (`pw`=week, `pm`=month, `py`=year)
- `country=US` — Country code
- `safesearch=moderate` — `off`, `moderate`, `strict`
- `offset=N` — Pagination

## Example: Recent AI News

```bash
curl -s -G "https://api.search.brave.com/res/v1/news/search" \
  -H "X-Subscription-Token: BSAF1ntdKw1-W42GzQYb8FNN93Zsd6u" \
  --data-urlencode "q=AI technology news" \
  --data-urlencode "count=5" \
  --data-urlencode "freshness=pd" | jq -r '.results[] | "url: \(.url)\ntitle: \(.title)\nsnippet: \(.description // "")\n---"'
```

## Guardrails

- Max 20 results per call.
- Always use `jq` to keep output concise and readable.
- The full curl+jq pipeline should be a single `run_command` call.
