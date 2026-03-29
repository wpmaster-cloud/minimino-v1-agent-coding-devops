---
name: cloudflare
description: "Manage Cloudflare zones, DNS, Workers, Pages, KV, and R2 via the REST API. Use when the mission involves Cloudflare DNS, CDN, Workers, or any Cloudflare service."
---

# Cloudflare API

Use this skill when the mission requires managing Cloudflare resources via the REST API.

## Prerequisites

- `CF_API_TOKEN` must be set in `.env` with appropriate permission scopes.
- Verify before starting: `curl -s -H "Authorization: Bearer $CF_API_TOKEN" https://api.cloudflare.com/client/v4/user/tokens/verify | jq .success`

## Auth

```bash
# API Token (recommended)
-H "Authorization: Bearer $CF_API_TOKEN"

# Legacy API Key (avoid)
-H "X-Auth-Email: $CF_EMAIL" -H "X-Auth-Key: $CF_API_KEY"
```

## Response format

All endpoints return:
```json
{"success": true, "errors": [], "messages": [], "result": {...}, "result_info": {"page": 1, "per_page": 20, "total_count": 100}}
```
Always check `success` field. Errors are in the `errors` array.

## Workflow

1. **Verify token** — Check token validity (see Prerequisites).
2. **Discover IDs** — Get Zone ID, Account ID, or Record IDs first.
3. **Read** — GET to inspect current state.
4. **Mutate** — POST/PUT/PATCH/DELETE.
5. **Verify** — GET again to confirm.

## Discover IDs

```bash
# Get Zone ID by domain name
curl -s "https://api.cloudflare.com/client/v4/zones?name=example.com" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[0].id'

# Account ID is in zone response too
curl -s "https://api.cloudflare.com/client/v4/zones?name=example.com" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[0].account.id'

# DNS Record ID
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=sub.example.com" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[0].id'
```

## Common operations

**DNS Records:**
```bash
# List all DNS records
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[] | {name, type, content}'

# Create A record
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"A","name":"sub.example.com","content":"1.2.3.4","ttl":3600,"proxied":true}'

# Update record
curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"A","name":"sub.example.com","content":"5.6.7.8","ttl":3600,"proxied":true}'

# Delete record
curl -s -X DELETE "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN"
```

**Zones:**
```bash
# List zones
curl -s "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[] | {name, id, status}'

# Purge cache (entire zone)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"purge_everything":true}'

# Purge specific URLs
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"files":["https://example.com/style.css"]}'
```

**Workers:**
```bash
# List workers
curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[].id'

# Upload worker (ES module format)
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts/$SCRIPT_NAME" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/javascript" \
  --data-binary @worker.js

# Delete worker
curl -s -X DELETE "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts/$SCRIPT_NAME" \
  -H "Authorization: Bearer $CF_API_TOKEN"
```

**KV:**
```bash
# List namespaces
curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/storage/kv/namespaces" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# Read a key
curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/storage/kv/namespaces/$NS_ID/values/$KEY" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# Write a key
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/storage/kv/namespaces/$NS_ID/values/$KEY" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  --data-binary "value"
```

**R2 (bucket management):**
```bash
# List buckets
curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/r2/buckets" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# R2 object operations use the S3-compatible API, not the v4 REST API.
```

**Pages:**
```bash
# List projects
curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[].name'

# Get deployments
curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects/$PROJECT/deployments" \
  -H "Authorization: Bearer $CF_API_TOKEN"
```

## Pagination

Use `page` and `per_page` query params. Check `result_info.total_pages` to know when to stop.

## Guardrails

- Always verify the token first.
- Always discover Zone ID / Account ID before making targeted calls.
- Rate limit: 1,200 requests per 5 minutes across all tokens. HTTP 429 blocks all calls for the window.
- A/AAAA records cannot coexist with CNAME on the same name.
- DNS `ttl` range: 60-86400, or `1` for automatic (proxied records ignore TTL).
- Use `--data-binary` (not `-d`) when uploading binary content.
- R2 object ops use S3-compatible API, not the v4 REST API.
- Worker uploads for ES modules use `multipart/form-data` with metadata.
- Always check `.success` in the response — HTTP 200 does not guarantee success.
