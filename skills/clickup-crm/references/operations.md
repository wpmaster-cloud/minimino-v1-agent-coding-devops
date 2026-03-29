# ClickUp CRM Operations Reference
 
Detailed code examples for all CRM CRUD operations. Read this file when the user asks to
create, read, update, or delete CRM records in ClickUp.
 
## Table of Contents
1. [Setup: Create CRM Space from Scratch](#1-setup-create-crm-space-from-scratch)
2. [Contacts: Create & Manage](#2-contacts-create--manage)
3. [Companies: Create & Manage](#3-companies-create--manage)
4. [Deals: Create & Manage](#4-deals-create--manage)
5. [Update Deal Stage (Pipeline)](#5-update-deal-stage-pipeline)
6. [Log Activity / Notes](#6-log-activity--notes)
7. [Link Records (Relationships)](#7-link-records-relationships)
8. [Search & Filter](#8-search--filter)
9. [Bulk Operations](#9-bulk-operations)
10. [Delete Records](#10-delete-records)
 
---
 
## 1. Setup: Create CRM Space from Scratch
 
```bash
# Step 1: Create the CRM Space
CREATE_SPACE=$(curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/team/$TEAM_ID/space \
  -d '{
    "name": "CRM",
    "multiple_assignees": true,
    "features": {
      "due_dates": {"enabled": true, "start_date": true},
      "priorities": {"enabled": true},
      "tags": {"enabled": true},
      "custom_fields": {"enabled": true}
    }
  }')
SPACE_ID=$(echo $CREATE_SPACE | jq -r '.space.id')
 
# Step 2: Create Deals list (with pipeline statuses)
CREATE_DEALS=$(curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/space/$SPACE_ID/list \
  -d '{
    "name": "Deals",
    "status": "active"
  }')
DEALS_LIST_ID=$(echo $CREATE_DEALS | jq -r '.id')
 
# Step 3: Create Contacts list
CREATE_CONTACTS=$(curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/space/$SPACE_ID/list \
  -d '{"name": "Contacts", "status": "active"}')
CONTACTS_LIST_ID=$(echo $CREATE_CONTACTS | jq -r '.id')
 
# Step 4: Create Companies list
CREATE_COMPANIES=$(curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/space/$SPACE_ID/list \
  -d '{"name": "Companies", "status": "active"}')
COMPANIES_LIST_ID=$(echo $CREATE_COMPANIES | jq -r '.id')
 
echo "Space: $SPACE_ID | Deals: $DEALS_LIST_ID | Contacts: $CONTACTS_LIST_ID | Companies: $COMPANIES_LIST_ID"
```
 
> **Note**: Pipeline statuses (Qualified, Proposal Sent, etc.) must be set in the ClickUp UI
> after list creation. The API does not currently support creating custom statuses per-list.
> Direct users to: List Settings → Statuses → Add custom stages.
 
---
 
## 2. Contacts: Create & Manage
 
### Create a contact
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$CONTACTS_LIST_ID/task \
  -d '{
    "name": "Jane Smith",
    "description": "Met at SaaStr 2025",
    "priority": 2,
    "assignees": [],
    "tags": ["hot-lead"],
    "custom_fields": []
  }'
```
 
### Get all contacts (paginated)
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/list/$CONTACTS_LIST_ID/task?page=0&order_by=created&reverse=true" \
  | jq '.tasks[] | {id, name, status: .status.status, created: .date_created}'
```
 
### Get a single contact
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/task/$TASK_ID \
  | jq '{id, name, description, custom_fields, assignees, tags}'
```
 
### Update a contact
```bash
curl -s -X PUT \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID \
  -d '{
    "name": "Jane Smith (Updated)",
    "description": "Senior VP at Acme Corp"
  }'
```
 
### Set a custom field on a contact (e.g., email)
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": "jane@acme.com"}'
```
 
---
 
## 3. Companies: Create & Manage
 
### Create a company
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$COMPANIES_LIST_ID/task \
  -d '{
    "name": "Acme Corporation",
    "description": "Enterprise software company, 500 employees",
    "priority": 2
  }'
```
 
### Recommended custom fields for Companies:
See `custom-fields.md` → Companies section.
 
---
 
## 4. Deals: Create & Manage
 
### Create a deal
```bash
DEAL=$(curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task \
  -d '{
    "name": "Acme Corp — Enterprise License",
    "status": "New Lead",
    "priority": 2,
    "due_date": 1746057600000,
    "assignees": [12345678],
    "tags": ["enterprise"],
    "description": "Initial contact via LinkedIn. Budget $50k ARR."
  }')
DEAL_ID=$(echo $DEAL | jq -r '.id')
echo "Created deal: $DEAL_ID"
```
 
### Create deal with all CRM custom fields in one shot
```bash
# First get the field IDs for your list
FIELDS=$(curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/field)
echo $FIELDS | jq '.fields[] | {id, name, type}'
 
# Then create task (set fields separately via /field/{id} endpoint after creation)
```
 
---
 
## 5. Update Deal Stage (Pipeline)
 
### Move a deal to a new stage
```bash
curl -s -X PUT \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$DEAL_ID \
  -d '{"status": "Qualified"}'
```
 
### Pipeline stage progression helper (bash function)
```bash
advance_deal() {
  local deal_id="$1"
  local new_stage="$2"  # e.g. "Proposal Sent", "Closed Won", "Closed Lost"
  curl -s -X PUT \
    -H "Authorization: $CLICKUP_API_TOKEN" \
    -H "Content-Type: application/json" \
    https://api.clickup.com/api/v2/task/$deal_id \
    -d "{\"status\": \"$new_stage\"}" \
    | jq '{id, name, status: .status.status}'
}
 
# Usage
advance_deal "abc123def" "Proposal Sent"
advance_deal "abc123def" "Closed Won"
```
 
### Mark as Closed Lost with reason
```bash
# Update status + add closing note
curl -s -X PUT \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$DEAL_ID \
  -d '{"status": "Closed Lost"}'
 
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$DEAL_ID/comment \
  -d '{"comment_text": "Lost to competitor. Price was the deciding factor.", "notify_all": false}'
```
 
---
 
## 6. Log Activity / Notes
 
### Add a call log / meeting note
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/comment \
  -d '{
    "comment_text": "📞 Call 2025-04-01\n\nSpoke with Jane Smith. She confirmed budget of $40k. Needs proposal by Friday. Next: send proposal doc.",
    "notify_all": false
  }'
```
 
### Get all activity on a deal
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/task/$TASK_ID/comment \
  | jq '.comments[] | {date: .date, text: .comment_text, by: .user.username}'
```
 
### Set a follow-up due date
```bash
# Convert date to ms timestamp first
DUE_MS=$(date -d "2025-04-07" +%s000)
curl -s -X PUT \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID \
  -d "{\"due_date\": $DUE_MS, \"due_date_time\": false}"
```
 
### Create a follow-up subtask
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task \
  -d "{
    \"name\": \"Follow up with Jane Smith — send proposal\",
    \"parent\": \"$DEAL_ID\",
    \"due_date\": $DUE_MS,
    \"priority\": 1
  }"
```
 
---
 
## 7. Link Records (Relationships)
 
ClickUp relationships are stored as custom fields of type `relationship`. Once created in the UI
or via API, they link task IDs across lists.
 
### Get relationship field ID
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/field \
  | jq '.fields[] | select(.type == "relationship") | {id, name}'
```
 
### Link a deal to a company
```bash
# RELATION_FIELD_ID is the relationship custom field on Deals pointing to Companies
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$DEAL_ID/field/$RELATION_FIELD_ID \
  -d "{\"value\": {\"add\": [\"$COMPANY_TASK_ID\"]}}"
```
 
### Link a deal to a contact
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$DEAL_ID/field/$CONTACT_RELATION_FIELD_ID \
  -d "{\"value\": {\"add\": [\"$CONTACT_TASK_ID\"]}}"
```
 
### Add a task dependency (e.g., proposal depends on discovery call)
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/dependency \
  -d "{\"depends_on\": \"$DEPENDENCY_TASK_ID\", \"dependency_of\": null}"
```
 
---
 
## 8. Search & Filter
 
### Filter deals by status
```bash
# URL-encode status with %20 for spaces
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?statuses[]=Qualified&statuses[]=Proposal%20Sent" \
  | jq '.tasks[] | {id, name, status: .status.status}'
```
 
### Filter across workspace (all lists) by assignee
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/team/$TEAM_ID/task?assignees[]=$USER_ID&space_ids[]=$SPACE_ID" \
  | jq '.tasks[] | {id, name, status: .status.status, list: .list.name}'
```
 
### Filter by due date range (overdue deals)
```bash
NOW_MS=$(date +%s000)
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?due_date_lt=$NOW_MS&include_closed=false" \
  | jq '.tasks[] | {id, name, due: .due_date, status: .status.status}'
```
 
### Filter by custom field value (deals over $10k)
```bash
# Build the custom_fields JSON filter, URL encode it
FILTER='[{"field_id":"YOUR_DEAL_VALUE_FIELD_ID","operator":">=","value":"10000"}]'
ENCODED=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$FILTER")
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?custom_fields=$ENCODED" \
  | jq '.tasks[] | {id, name}'
```
 
### Search contacts by name (client-side filter)
```bash
SEARCH_NAME="Jane"
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/list/$CONTACTS_LIST_ID/task?page=0" \
  | jq --arg name "$SEARCH_NAME" \
    '.tasks[] | select(.name | test($name; "i")) | {id, name}'
```
 
---
 
## 9. Bulk Operations
 
### Bulk update deal stage (multiple task IDs)
```bash
DEAL_IDS=("abc123" "def456" "ghi789")
NEW_STATUS="Proposal Sent"
for id in "${DEAL_IDS[@]}"; do
  curl -s -X PUT \
    -H "Authorization: $CLICKUP_API_TOKEN" \
    -H "Content-Type: application/json" \
    https://api.clickup.com/api/v2/task/$id \
    -d "{\"status\": \"$NEW_STATUS\"}" > /dev/null
  echo "Updated $id"
  sleep 0.5  # respect rate limits
done
```
 
### Export all deals to JSON
```bash
PAGE=0
ALL_DEALS=()
while true; do
  RESULT=$(curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
    "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?page=$PAGE&include_closed=true")
  COUNT=$(echo $RESULT | jq '.tasks | length')
  [ "$COUNT" -eq 0 ] && break
  echo $RESULT | jq '.tasks[]' >> /tmp/all_deals.jsonl
  PAGE=$((PAGE+1))
done
echo "Exported $(wc -l < /tmp/all_deals.jsonl) deals"
```
 
### Import contacts from CSV (bash + jq)
```bash
# Expects CSV: name,email,company,phone
tail -n +2 contacts.csv | while IFS=',' read -r name email company phone; do
  curl -s -X POST \
    -H "Authorization: $CLICKUP_API_TOKEN" \
    -H "Content-Type: application/json" \
    https://api.clickup.com/api/v2/list/$CONTACTS_LIST_ID/task \
    -d "{\"name\": \"$name\", \"description\": \"Company: $company\"}" > /dev/null
  echo "Imported: $name"
  sleep 0.6  # stay under rate limit
done
```
 
---
 
## 10. Delete Records
 
```bash
# Delete a single task (contact/deal/company)
curl -s -X DELETE \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/task/$TASK_ID
 
# Bulk delete (with confirmation)
for id in $TASK_IDS; do
  echo "Deleting $id..."
  curl -s -X DELETE -H "Authorization: $CLICKUP_API_TOKEN" \
    https://api.clickup.com/api/v2/task/$id
  sleep 0.5
done
```
 
> ⚠️ Deletions are permanent. Always confirm with the user before bulk deleting.