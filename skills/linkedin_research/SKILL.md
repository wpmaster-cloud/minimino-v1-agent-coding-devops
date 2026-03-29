---
name: linkedin_research
description: "Research LinkedIn profiles, companies, job postings, and company posts. Use when the mission involves LinkedIn, professional research, company info, or job market analysis."
---

# LinkedIn Research skill

Use this skill when the mission involves looking up LinkedIn profiles, companies, job postings, or searching for jobs.

## Goal

Use the LinkedIn Scraper MCP tools to gather professional data from LinkedIn.

## Available MCP tools

- `linkedin_check_auth` — Verify authentication status. Params: `force_reauth` (optional bool).
- `linkedin_scrape_person` — Scrape a person's profile. Params: `profile_url` (required), `force_reauth` (optional).
- `linkedin_scrape_company` — Scrape a company page. Params: `company_url` (required), `force_reauth` (optional).
- `linkedin_scrape_company_posts` — Scrape recent company posts. Params: `company_url` (required), `limit` (optional, default 10), `force_reauth` (optional).
- `linkedin_scrape_job` — Scrape a specific job posting. Params: `job_url` (required), `force_reauth` (optional).
- `linkedin_search_jobs` — Search for jobs. Params: `keywords` (optional), `location` (optional), `limit` (optional, default 10), `scrape_details` (optional bool), `force_reauth` (optional).

## Exact workflow

1. **Check auth** — Always call `linkedin_check_auth` first to verify the scraper is authenticated.
   - If auth fails, try with `force_reauth: true` once.
   - If still failing → `stuck` with auth error.
2. **Scrape the target**:
   - Person: `linkedin_scrape_person` with full profile URL (e.g. `https://www.linkedin.com/in/username/`)
   - Company: `linkedin_scrape_company` with full company URL (e.g. `https://www.linkedin.com/company/name/`)
   - Job: `linkedin_scrape_job` with full job URL
   - Job search: `linkedin_search_jobs` with keywords and optional location
3. **Extract and format** — Pull out relevant fields from the response (name, title, company, experience, skills, job details, etc.).
4. **Deliver** — Format as requested (summary, JSON, table) and deliver via Telegram, file, or Notion.

## Common patterns

### Person research
```
linkedin_check_auth
linkedin_scrape_person with profile_url: "https://www.linkedin.com/in/username/"
```
Extract: name, headline, current role, experience history, education, skills.

### Company overview
```
linkedin_scrape_company with company_url: "https://www.linkedin.com/company/name/"
linkedin_scrape_company_posts with company_url: "https://www.linkedin.com/company/name/" limit: 5
```
Combine company info with recent activity for a full picture.

### Job search
```
linkedin_search_jobs with keywords: "software engineer" location: "Tel Aviv" limit: 10 scrape_details: true
```
Set `scrape_details: true` to get full job descriptions, not just titles.

## Guardrails

- Always check auth before any scrape operation.
- Use full LinkedIn URLs, not just usernames or company names.
- LinkedIn rate-limits aggressively. Keep `limit` reasonable (10–20). Do not scrape 100+ profiles in a single mission.
- If a scrape returns empty or an error, try `force_reauth: true` once. If still failing, the profile may be private or the URL incorrect.
- Do not scrape profiles for purposes the mission doesn't explicitly require.
- Same error twice → `stuck`.
