---
name: clickup-crm
description: >
  Use ClickUp as a full-featured CRM via its REST API. Trigger this skill whenever the user wants
  to manage contacts, leads, deals, accounts, or sales pipelines in ClickUp — including setup,
  querying, creating records, updating deal stages, tracking follow-ups, building pipeline views,
  running reports, or automating CRM workflows. Use this skill even if the user just says things
  like "add a lead to ClickUp", "move the deal to Closed Won", "show me the pipeline", "log a
  call with a contact", "set up a CRM in ClickUp", or "find all deals over $10k". Any sales,
  contact management, or account tracking task involving ClickUp should use this skill.
compatibility:
  tools: [bash, web_fetch]
  auth: ClickUp Personal API Token (env var CLICKUP_API_TOKEN) or prompt user
---
 
# ClickUp CRM Skill
 
A complete guide for using ClickUp as a CRM via its REST API — covering setup, daily operations,
reporting, and automation.
 
## Table of Contents
1. [Authentication & Setup](#1-authentication--setup)
2. [CRM Architecture](#2-crm-architecture)
3. [Core API Patterns](#3-core-api-patterns)
4. [CRM Operations Reference](#4-crm-operations-reference) → see `references/operations.md`
5. [Custom Fields for CRM](#5-custom-fields-for-crm) → see `references/custom-fields.md`
6. [Pipeline & Views](#6-pipeline--views)
7. [Reporting & Dashboards](#7-reporting--dashboards)
8. [Automation Patterns](#8-automation-patterns)
9. [Error Handling](#9-error-handling)
 
---
 
## 1. Authentication & Setup
 
### Get your API token
Settings → Apps → API Token (in ClickUp UI)
 
### Every API request needs this header:
```
Authorization: <your_token>
Content-Type: application/json
```
Base URL: `https://api.clickup.com/api/v2`
 
### First call — discover your workspace ID:
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/team \
  | jq '.teams[] | {id, name}'
```
Store the `team_id` (also called workspace_id). You'll need it for most calls.
 
### Find your CRM Space and List IDs:
```bash
# List all spaces
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/team/$TEAM_ID/space?archived=false \
  | jq '.spaces[] | {id, name}'
 
# List all lists in a space (flat, no folders)
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/space/$SPACE_ID/list?archived=false \
  | jq '.lists[] | {id, name}'
```
 
> **Tip**: If the user hasn't set up a CRM yet, follow Section 2 to scaffold one.
 
---
 
## 2. CRM Architecture
 
### Recommended hierarchy (ClickUp's own best practice):
 
```
Workspace
└── Space: "CRM" or "Sales"
    ├── List: Leads          ← inbound inquiries, unqualified contacts
    ├── List: Contacts       ← people (linked to Companies)
    ├── List: Companies      ← account/company records
    └── List: Deals          ← opportunities with pipeline stages
```
 
**Statuses for the Deals list** (pipeline stages):
- `New Lead` → `Qualified` → `Proposal Sent` → `Negotiation` → `Closed Won` → `Closed Lost`
 
**Alternative (simpler):** Skip separate Contacts/Companies lists, embed contact info
as custom fields directly on Deals. Good for solo users or small teams.
 
### Scaffold a new CRM Space via API:
See `references/operations.md` → "Setup: Create CRM Space from Scratch"
 
### Custom Fields to add:
See `references/custom-fields.md` for full field definitions and `type_config` payloads.
 
---
 
## 3. Core API Patterns
 
### Task = CRM Record
In ClickUp, every Contact, Company, Deal, and Lead is a **task**. "Task" and "record" are
interchangeable in this context.
 
### Key endpoints:
| Action | Method | Endpoint |
|--------|--------|----------|
| List tasks (records) | GET | `/list/{list_id}/task` |
| Get single task | GET | `/task/{task_id}` |
| Create task | POST | `/list/{list_id}/task` |
| Update task | PUT | `/task/{task_id}` |
| Delete task | DELETE | `/task/{task_id}` |
| Set custom field | POST | `/task/{task_id}/field/{field_id}` |
| Get list custom fields | GET | `/list/{list_id}/field` |
| Add comment/note | POST | `/task/{task_id}/comment` |
| Filter tasks | GET | `/team/{team_id}/task` with query params |
 
### Pagination:
All list endpoints support `?page=0&order_by=created&reverse=true`. Default page size is 100.
 
### Date format:
All dates are **Unix timestamps in milliseconds** (e.g., `1710000000000`). Convert:
```bash
date -d "2025-04-01" +%s000   # Linux
```
 
---
 
## 4. CRM Operations Reference
 
**For detailed code examples on all CRUD operations**, read:
```
references/operations.md
```
Covers: create contact, create deal, update stage, log activity, search/filter, link records,
bulk update, delete, and setup from scratch.
 
---
 
## 5. Custom Fields for CRM
 
**For field type definitions, payloads, and CRM-specific field recommendations**, read:
```
references/custom-fields.md
```
Covers: all ClickUp field types, recommended fields per list (Deals, Contacts, Companies),
how to create and set fields via API.
 
---
 
## 6. Pipeline & Views
 
### Board view = your visual pipeline
The Deals list in Board view, grouped by **status**, gives you a Kanban pipeline.
Create it via the ClickUp UI or encourage users to set it up manually (Views API is limited
for creation; use the UI for initial view setup).
 
### Key views to recommend to users:
| View | Purpose |
|------|---------|
| Board (by status) | Visual pipeline — drag deals through stages |
| Table | Spreadsheet-style; bulk edit custom fields |
| List | Prioritized task list; filter by owner |
| Calendar | Follow-up dates, renewal dates |
 
### Filtering tasks via API:
```bash
# Deals owned by a specific assignee, in a status, over a date range
curl -s -H "Authorization: $TOKEN" \
  "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?\
status=Qualified&assignees[]=$USER_ID&due_date_gt=1710000000000" \
  | jq '.tasks[] | {id, name, status: .status.status}'
```
 
### Filter by custom field value:
Use `custom_fields` query param (JSON-encoded):
```
?custom_fields=[{"field_id":"<id>","operator":">=","value":"10000"}]
```
See `references/operations.md` → "Search & Filter" for full examples.
 
---
 
## 7. Reporting & Dashboards
 
### Pipeline value summary (shell):
```bash
# Sum deal values from custom field across all Deals
curl -s -H "Authorization: $TOKEN" \
  "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?include_closed=true" \
  | jq '[.tasks[] | select(.custom_fields[] | .name == "Deal Value") |
      .custom_fields[] | select(.name == "Deal Value") | .value // 0 | tonumber] | add'
```
 
### Deals by stage count:
```bash
curl -s -H "Authorization: $TOKEN" \
  "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?include_closed=true" \
  | jq '[.tasks[] | {stage: .status.status}] | group_by(.stage) |
      map({stage: .[0].stage, count: length})'
```
 
### For richer dashboards:
- Use ClickUp Dashboards UI (not available via API for creation)
- Export task data to CSV, then analyze externally
- Integrate with Google Sheets or Notion via Make/Zapier
 
---
 
## 8. Automation Patterns
 
ClickUp's native Automations (UI only) cover common CRM triggers. For API-driven automation:
 
### Webhook: listen for status changes
```bash
# Register a webhook on your workspace
curl -s -X POST -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/team/$TEAM_ID/webhook \
  -d '{
    "endpoint": "https://your-server.com/webhook",
    "events": ["taskStatusUpdated", "taskCreated", "taskUpdated"],
    "space_id": '$SPACE_ID'
  }'
```
 
Webhook payload includes `task_id`, `history_items` (before/after values), and `event` type.
 
### Common automation triggers via API polling:
- **Follow-up reminder**: find deals with `due_date` in past and status not Closed → create
  subtask or post comment
- **Stage auto-advance**: after a checklist item is completed, update task status
- **Deal owner assignment**: on task creation in Leads list, assign to round-robin user
 
---
 
## 9. Error Handling
 
| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 401 | Invalid/missing token | Check `Authorization` header |
| 403 | No access to resource | Verify token has permission to that Space/List |
| 404 | Resource not found | Confirm list_id, task_id, field_id |
| 429 | Rate limit exceeded | Back off; free plans get ~100 req/min |
| 500 | ClickUp server error | Retry after 5s |
 
### Rate limits:
- Free: ~100 requests/minute
- Paid plans: higher, varies by tier
- Always check `X-RateLimit-Remaining` response header
 
### Robust curl wrapper (bash):
```bash
clickup_get() {
  local url="$1"
  local response
  response=$(curl -s -w "\n%{http_code}" -H "Authorization: $CLICKUP_API_TOKEN" "$url")
  local body=$(echo "$response" | head -n -1)
  local code=$(echo "$response" | tail -n 1)
  if [ "$code" != "200" ]; then
    echo "ERROR $code: $body" >&2; return 1
  fi
  echo "$body"
}
```
 
---
 
## Quick Reference Cheatsheet
 
```bash
# Environment (set once)
export CLICKUP_API_TOKEN="pk_..."
export TEAM_ID="..."          # workspace id
export SPACE_ID="..."         # CRM space id
export DEALS_LIST="..."       # Deals list id
export CONTACTS_LIST="..."    # Contacts list id
export COMPANIES_LIST="..."   # Companies list id
 
# Discover IDs
curl -s -H "Authorization: $CLICKUP_API_TOKEN" https://api.clickup.com/api/v2/team | jq .
curl -s -H "Authorization: $CLICKUP_API_TOKEN" https://api.clickup.com/api/v2/team/$TEAM_ID/space?archived=false | jq .
curl -s -H "Authorization: $CLICKUP_API_TOKEN" https://api.clickup.com/api/v2/space/$SPACE_ID/list | jq .
 
# Quick actions
# Create lead
curl -X POST -H "Authorization: $CLICKUP_API_TOKEN" -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$DEALS_LIST/task \
  -d '{"name":"Acme Corp","status":"New Lead","priority":2}'
 
# Move to next stage
curl -X PUT -H "Authorization: $CLICKUP_API_TOKEN" -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID \
  -d '{"status":"Qualified"}'
 
# Log a note
curl -X POST -H "Authorization: $CLICKUP_API_TOKEN" -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/comment \
  -d '{"comment_text":"Called John — interested, follow up Friday","notify_all":false}'
```