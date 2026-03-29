---
name: web_browsing
description: "Browse live websites, fill forms, click buttons, and extract dynamic content via browser automation. Use when a site requires JavaScript rendering, login, or multi-step interaction."
---

# Web Browsing (Scraper) skill

Use this skill to scrape the full content of any web page via the Firecrawl API.

## API Configuration

**Endpoint**: `https://api.firecrawl.dev/v1/scrape`  
**API Key**: `fc-a901d7717a0c445d8ccf36270569b505` (Hardcoded)

## Usage

Always use `curl` with `run_command`. Use `jq` to extract the content.

### Scrape Page to Markdown

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Authorization: Bearer fc-a901d7717a0c445d8ccf36270569b505" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown"],
    "scrapeOptions": { "onlyMainContent": true }
  }' | jq -r '.data.markdown'
```

### Scrape to Plain Text

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Authorization: Bearer fc-a901d7717a0c445d8ccf36270569b505" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown"]
  }' | jq -r '.data.markdown' | sed 's/[*_`#>~|]//g'
```

## Options

- `"onlyMainContent": true` — Strip nav/footer (recommended).
- `"formats": ["links"]` — Get all links instead of content.

## Guardrails

- Always use the hardcoded API key provided.
- Firecrawl is best for JS-heavy sites or when `read_url_content` fails.

## Available MCP tools

- `browse_and_act` — Navigate to a URL and autonomously accomplish a goal using vision. Takes screenshots, analyzes them with a vision model, and executes actions (click, type, scroll, keypress) step by step. Params: `url` (required), `goal` (required), `max_steps` (optional, default 15).
- `browse_navigate` — Navigate the browser to a URL. Params: `url` (required).
- `browse_screenshot` — Take a screenshot of the current page. Set `describe` to `"true"` to get a text description instead of base64. Params: `describe` (optional).
- `browse_status` — Get the current browser URL and page title. No params.

## When to use which tool

- **`browse_and_act`** — Full autonomous browsing: "go to this site and find X" or "fill out this form." The vision model drives the interaction loop.
- **`browse_navigate` + `browse_screenshot`** — Manual step-by-step browsing when you need to inspect a page before deciding what to do. Use `describe: "true"` to read page content as text.
- **`browse_status`** — Check where the browser is currently pointed.

## Workflow

1. **Define the goal** — Be specific about what needs to happen on the page.
2. **Choose the approach**:
   - Simple extraction → `browse_navigate` + `browse_screenshot` with `describe: "true"`
   - Multi-step interaction → `browse_and_act` with a clear goal
3. **Set max_steps** — Default is 15. Increase for complex multi-page flows (e.g. `"25"`). Keep low for simple tasks (e.g. `"5"`).
4. **Process the result** — `browse_and_act` returns a summary of actions taken and outcome. Use this in your report.

## Common patterns

### Read page content
```
browse_navigate → url: "https://example.com/page"
browse_screenshot → describe: "true"
```
Returns a text description of the page contents.

### Fill and submit a form
```
browse_and_act → url: "https://example.com/form", goal: "Fill in name as 'John Doe', email as 'john@example.com', then click Submit"
```
The vision model handles finding fields, typing, and clicking.

### Multi-page research
```
browse_and_act → url: "https://news.example.com", goal: "Find the top 3 headlines about AI and note their titles and dates", max_steps: "20"
```

## Guardrails

- The browser runs headless Chromium in the cluster. No GUI is visible.
- Vision model interprets screenshots — it can misidentify UI elements. If `browse_and_act` gets stuck, try a more specific goal or break into manual steps.
- Max steps caps the vision loop. If it reaches the limit without completing, increase `max_steps` or simplify the goal.
- Login-protected pages require credentials passed in the goal text. Never store passwords in memory.
- The browser has no access to the agent workspace filesystem. To save scraped content, capture the tool output and use `write_file`.
- For simple web scraping (no interaction needed), prefer `web_scraper.sh` over the browser — it's faster and more reliable.
- Each `browse_and_act` call starts a fresh navigation. The browser state (cookies, session) may persist between calls within the same MCP pod lifecycle.
