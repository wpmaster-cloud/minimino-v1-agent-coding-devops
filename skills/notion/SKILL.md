# Notion

Interact with the Notion API using the Python CLI tool.

## Usage

All commands require `NOTION_TOKEN` to be set in the environment. Use `run_command` to execute.

| Command | Purpose |
|------|---------|
| `python3 scripts/notion_tool.py search "query"` | Search pages and databases |
| `python3 scripts/notion_tool.py get_page PAGE_ID` | Retrieve page metadata |
| `python3 scripts/notion_tool.py get_blocks BLOCK_ID` | List child blocks (content) |
| `python3 scripts/notion_tool.py create_page --parent '{"page_id":"..."}' --properties '{"title":[{"text":{"content":"..."}}]}'` | Create a page |
| `python3 scripts/notion_tool.py update_page PAGE_ID --properties '...'` | Update properties |
| `python3 scripts/notion_tool.py query_database DATABASE_ID` | Query a database |

## Workflow

### Creating a page
1. **Find the parent** — Use `search` to find the target page or database ID.
2. **Create** — Use `create_page` with `--parent` and `--properties`. Note that properties must match the target schema.

### Reading content
1. **Search** — Use `search` to find the page ID.
2. **Get body** — Use `get_blocks` with the page ID to read the content blocks.

### Querying a database
1. **Query** — Use `query_database` with optional `--filter` and `--sorts` (JSON strings).

## Key Patterns

- **Parent**: `'{"page_id": "..."}'` or `'{"database_id": "..."}'`.
- **Title property**: `'{"title": [{"text": {"content": "New Page"}}] }'`.
- **JSON Arguments**: Always wrap JSON strings in single quotes `'{"key": "value"}'` to avoid shell escaping issues.

## Examples

**Search for a page:**
```bash
python3 scripts/notion_tool.py search "Project Alpha"
```

**Create a simple page:**
```bash
python3 scripts/notion_tool.py create_page --parent '{"page_id": "YOUR_PAGE_ID"}' --properties '{"title": [{"text": {"content": "Meeting Notes"}}] }'
```

## Guardrails

- The integration can only access pages explicitly shared with it in Notion.
- Always check the JSON syntax before running commands.
- Use `jq` to filter the large output if necessary.
