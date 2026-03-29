# ClickUp CRM Custom Fields Reference
 
Everything you need to create and set custom fields for CRM lists in ClickUp.
 
## Table of Contents
1. [Field Types Overview](#1-field-types-overview)
2. [Create a Custom Field](#2-create-a-custom-field)
3. [Recommended Fields: Deals List](#3-recommended-fields-deals-list)
4. [Recommended Fields: Contacts List](#4-recommended-fields-contacts-list)
5. [Recommended Fields: Companies List](#5-recommended-fields-companies-list)
6. [Set / Update Field Values](#6-set--update-field-values)
7. [Read Field Values from Tasks](#7-read-field-values-from-tasks)
 
---
 
## 1. Field Types Overview
 
| type string | Use for |
|-------------|---------|
| `text` | Short text (names, notes) |
| `email` | Email address (validated) |
| `phone` | Phone number |
| `url` | Website, LinkedIn profile |
| `number` | Integers, percentages |
| `currency` | Money amounts |
| `date` | Date picker |
| `checkbox` | Boolean true/false |
| `dropdown` | Single-select enum |
| `labels` | Multi-select tags |
| `relationship` | Link to tasks in another list |
| `users` | Assign ClickUp users |
| `rating` | 1–5 star rating |
| `location` | Map pin / address |
 
---
 
## 2. Create a Custom Field
 
### Basic text field
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$LIST_ID/field \
  -d '{
    "name": "LinkedIn URL",
    "type": "url",
    "required": false
  }'
```
 
### Dropdown field (pipeline-style)
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$LIST_ID/field \
  -d '{
    "name": "Lead Source",
    "type": "drop_down",
    "type_config": {
      "options": [
        {"name": "Inbound", "color": "#00C875"},
        {"name": "Outbound", "color": "#579BFC"},
        {"name": "Referral", "color": "#FFCB00"},
        {"name": "Event", "color": "#FF7575"},
        {"name": "LinkedIn", "color": "#0073B1"},
        {"name": "Cold Email", "color": "#C4C4C4"}
      ]
    },
    "required": false
  }'
```
 
### Currency field
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$LIST_ID/field \
  -d '{
    "name": "Deal Value",
    "type": "currency",
    "type_config": {
      "currency_type": "USD"
    }
  }'
```
 
### Number field (e.g., probability %)
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$LIST_ID/field \
  -d '{
    "name": "Close Probability %",
    "type": "number",
    "type_config": {
      "precision": 0,
      "separator": "period"
    }
  }'
```
 
### Relationship field (link Deals → Companies)
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/field \
  -d "{
    \"name\": \"Company\",
    \"type\": \"relationship\",
    \"type_config\": {
      \"linked_list_id\": \"$COMPANIES_LIST_ID\"
    }
  }"
```
 
---
 
## 3. Recommended Fields: Deals List
 
Run these to scaffold a standard CRM deals list. Capture the field IDs from each response.
 
```bash
BASE="https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/field"
H='-H "Authorization: $CLICKUP_API_TOKEN" -H "Content-Type: application/json"'
 
# Deal Value (currency)
curl -s -X POST $H $BASE -d '{"name":"Deal Value","type":"currency","type_config":{"currency_type":"USD"}}'
 
# Close Probability (number, 0-100)
curl -s -X POST $H $BASE -d '{"name":"Close Probability %","type":"number","type_config":{"precision":0}}'
 
# Expected Close Date (date)
curl -s -X POST $H $BASE -d '{"name":"Expected Close Date","type":"date"}'
 
# Lead Source (dropdown)
curl -s -X POST $H $BASE -d '{
  "name": "Lead Source",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"Inbound"},{"name":"Outbound"},{"name":"Referral"},
      {"name":"Event"},{"name":"LinkedIn"},{"name":"Cold Email"},{"name":"Partner"}
    ]
  }
}'
 
# Deal Type (dropdown)
curl -s -X POST $H $BASE -d '{
  "name": "Deal Type",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"New Business"},{"name":"Expansion"},{"name":"Renewal"},{"name":"Churn Prevention"}
    ]
  }
}'
 
# Health Score (dropdown)
curl -s -X POST $H $BASE -d '{
  "name": "Health Score",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"🟢 Green","color":"#00C875"},
      {"name":"🟡 Yellow","color":"#FFCB00"},
      {"name":"🔴 Red","color":"#FF3D00"}
    ]
  }
}'
 
# Lost Reason (dropdown, for Closed Lost)
curl -s -X POST $H $BASE -d '{
  "name": "Lost Reason",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"Price"},{"name":"Competitor"},{"name":"No Budget"},
      {"name":"No Decision"},{"name":"Timing"},{"name":"Features"}
    ]
  }
}'
 
# Services/Products (labels, multi-select)
curl -s -X POST $H $BASE -d '{
  "name": "Services",
  "type": "labels",
  "type_config": {
    "options": [
      {"label":"Enterprise License"},{"label":"Professional Services"},
      {"label":"Support Contract"},{"label":"Training"},{"label":"Add-on"}
    ]
  }
}'
 
# MRR (currency)
curl -s -X POST $H $BASE -d '{"name":"MRR","type":"currency","type_config":{"currency_type":"USD"}}'
 
# ARR (currency)
curl -s -X POST $H $BASE -d '{"name":"ARR","type":"currency","type_config":{"currency_type":"USD"}}'
 
# Next Step (text)
curl -s -X POST $H $BASE -d '{"name":"Next Step","type":"text"}'
 
# Relationship to Company
curl -s -X POST $H $BASE -d "{\"name\":\"Company\",\"type\":\"relationship\",\"type_config\":{\"linked_list_id\":\"$COMPANIES_LIST_ID\"}}"
 
# Relationship to Contact
curl -s -X POST $H $BASE -d "{\"name\":\"Primary Contact\",\"type\":\"relationship\",\"type_config\":{\"linked_list_id\":\"$CONTACTS_LIST_ID\"}}"
```
 
---
 
## 4. Recommended Fields: Contacts List
 
```bash
BASE="https://api.clickup.com/api/v2/list/$CONTACTS_LIST_ID/field"
 
curl -s -X POST $H $BASE -d '{"name":"Email","type":"email"}'
curl -s -X POST $H $BASE -d '{"name":"Phone","type":"phone"}'
curl -s -X POST $H $BASE -d '{"name":"Job Title","type":"text"}'
curl -s -X POST $H $BASE -d '{"name":"LinkedIn","type":"url"}'
curl -s -X POST $H $BASE -d '{"name":"Twitter/X","type":"url"}'
 
# Contact Type (dropdown)
curl -s -X POST $H $BASE -d '{
  "name": "Contact Type",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"Lead"},{"name":"Prospect"},{"name":"Customer"},
      {"name":"Partner"},{"name":"Churned"}
    ]
  }
}'
 
# Lead Temperature
curl -s -X POST $H $BASE -d '{
  "name": "Lead Temperature",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"🔥 Hot","color":"#FF3D00"},
      {"name":"♨️ Warm","color":"#FFCB00"},
      {"name":"❄️ Cold","color":"#579BFC"}
    ]
  }
}'
 
# Company relationship
curl -s -X POST $H $BASE -d "{\"name\":\"Company\",\"type\":\"relationship\",\"type_config\":{\"linked_list_id\":\"$COMPANIES_LIST_ID\"}}"
 
# Last Contacted (date)
curl -s -X POST $H $BASE -d '{"name":"Last Contacted","type":"date"}'
```
 
---
 
## 5. Recommended Fields: Companies List
 
```bash
BASE="https://api.clickup.com/api/v2/list/$COMPANIES_LIST_ID/field"
 
curl -s -X POST $H $BASE -d '{"name":"Website","type":"url"}'
curl -s -X POST $H $BASE -d '{"name":"Company Email","type":"email"}'
curl -s -X POST $H $BASE -d '{"name":"Phone","type":"phone"}'
curl -s -X POST $H $BASE -d '{"name":"Address","type":"location"}'
curl -s -X POST $H $BASE -d '{"name":"LinkedIn Company Page","type":"url"}'
curl -s -X POST $H $BASE -d '{"name":"Team Size","type":"number","type_config":{"precision":0}}'
curl -s -X POST $H $BASE -d '{"name":"Annual Revenue","type":"currency","type_config":{"currency_type":"USD"}}'
 
# Industry (dropdown)
curl -s -X POST $H $BASE -d '{
  "name": "Industry",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"SaaS"},{"name":"FinTech"},{"name":"Healthcare"},{"name":"E-Commerce"},
      {"name":"Manufacturing"},{"name":"Professional Services"},{"name":"Education"},
      {"name":"Media"},{"name":"Other"}
    ]
  }
}'
 
# Customer Stage
curl -s -X POST $H $BASE -d '{
  "name": "Customer Stage",
  "type": "drop_down",
  "type_config": {
    "options": [
      {"name":"Prospect"},{"name":"Active Customer"},
      {"name":"Churned"},{"name":"Partner"}
    ]
  }
}'
 
# Account Owner (users field)
curl -s -X POST $H $BASE -d '{"name":"Account Owner","type":"users","type_config":{}}'
 
# NPS Score (rating)
curl -s -X POST $H $BASE -d '{"name":"NPS Score","type":"rating","type_config":{"count":10}}'
 
# Contract Renewal Date
curl -s -X POST $H $BASE -d '{"name":"Contract Renewal Date","type":"date"}'
```
 
---
 
## 6. Set / Update Field Values
 
### Text, email, phone, url fields
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": "jane@acme.com"}'
```
 
### Number / currency field
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": 45000}'
```
 
### Dropdown field (use the option's orderindex or value)
```bash
# First get the field to see option IDs
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/list/$LIST_ID/field \
  | jq '.fields[] | select(.name == "Lead Source") | .type_config.options[]'
 
# Then set by orderindex (0-based)
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": 2}'  # index 2 = 3rd option
```
 
### Date field (unix ms)
```bash
DUE_MS=$(date -d "2025-06-30" +%s000)
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d "{\"value\": $DUE_MS}"
```
 
### Checkbox field
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": true}'
```
 
### Labels field (multi-select — pass array of option names)
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": ["Enterprise License", "Support Contract"]}'
```
 
### Relationship field (link to another task)
```bash
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": {"add": ["LINKED_TASK_ID_1", "LINKED_TASK_ID_2"]}}'
 
# Remove a linked task
curl -s -X POST \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID \
  -d '{"value": {"rem": ["LINKED_TASK_ID_1"]}}'
```
 
### Clear / remove a field value
```bash
curl -s -X DELETE \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/task/$TASK_ID/field/$FIELD_ID
```
 
---
 
## 7. Read Field Values from Tasks
 
### Get all custom field values for a task
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/task/$TASK_ID \
  | jq '.custom_fields[] | {name, type, value}'
```
 
### Extract a specific field value by name
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  https://api.clickup.com/api/v2/task/$TASK_ID \
  | jq '.custom_fields[] | select(.name == "Deal Value") | .value'
```
 
### Get all deals with their Deal Value field
```bash
curl -s -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/list/$DEALS_LIST_ID/task?include_closed=false" \
  | jq '.tasks[] | {
    name,
    stage: .status.status,
    value: (.custom_fields[] | select(.name == "Deal Value") | .value // 0)
  }'
```