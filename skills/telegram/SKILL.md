# Telegram skill

Use this skill to notify users or send files via the Telegram Bot API.

## API Configuration

**Bot Token**: `8730491849:AAFSs1nrda4tDkOJmo6OKDFiY_wQwb9fUjs` (Hardcoded)  
**Default Chat ID**: `535139005` (Hardcoded)

## Usage

Use `curl` to interact with the API directly. Always use `run_command`.

### Send Message

```bash
curl -s -X POST "https://api.telegram.org/bot8730491849:AAFSs1nrda4tDkOJmo6OKDFiY_wQwb9fUjs/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "535139005",
    "text": "YOUR_MESSAGE_HERE",
    "parse_mode": "Markdown"
  }'
```

### Send Photo/File

```bash
curl -s -X POST "https://api.telegram.org/bot8730491849:AAFSs1nrda4tDkOJmo6OKDFiY_wQwb9fUjs/sendPhoto" \
  -F "chat_id=535139005" \
  -F "photo=@path/to/image.png" \
  -F "caption=Optional caption"
```

## Guardrails

- Ensure the bot is added to the chat and has permission to send messages.
- Always use the hardcoded tokens provided above.
- For non-text content, use the appropriate endpoint (`sendDocument`, `sendVideo`, etc.).
