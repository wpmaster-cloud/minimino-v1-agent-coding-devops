---
name: temp_mail
description: "Generate a disposable temporary email address from temp-mail.org and retrieve incoming messages. Use when a throwaway email is needed for signups, verification, or testing."
---

# Temp Mail skill

Use this skill when the mission asks for a temporary email from https://temp-mail.org and then sending it to Telegram.

## Goal

Get the currently shown temp-mail address and send it through `./scripts/telegram.sh message`.

## Exact workflow

1. Open site in headed Playwright cloudflare mode first:
   - `./scripts/playwright_browser.sh "https://temp-mail.org/" open --cloudflare --headed`
   - Prefer non-blocking open behavior (warmup), do not wait forever.
2. Extract email directly from DOM value (preferred):
   - `./scripts/playwright_browser.sh "https://temp-mail.org/" eval --js="document.querySelector('input#mail')?.value || document.querySelector('#mail')?.value || ''" --cloudflare`
3. Validate candidate contains `@` and has no spaces/newlines.
4. If empty/invalid, run one fallback extraction only:
   - `./scripts/playwright_browser.sh "https://temp-mail.org/" text --cloudflare`
   - Parse first email-like token with regex pattern: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
5. Send to Telegram:
   - `./scripts/telegram.sh message "Temporary email address: <EMAIL>"`
6. Confirm Telegram response contains `"ok":true` before calling `done`.

## Guardrails

- Do not run repeated `text`/`html` loops when blocked signals are returned.
- Do not claim success without both: extracted non-empty email and successful Telegram API response.
- Use `stuck` if email extraction fails repeatedly or Telegram sending fails with the same error twice.
