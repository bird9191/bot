# Clean Clinic Bot Deployment

## Overview

The bot runs as a long-lived Python process:

```bash
python bot.py
```

QR traffic can point directly to the Telegram bot URL:

```text
https://t.me/Tests2609bot
```

Leads are saved to Google Sheets when Google Sheets variables are configured. A local `leads.csv` file is also used as a backup.

## Environment Variables

Required:

- `BOT_TOKEN` — Telegram bot token from BotFather.

Recommended:

- `ADMIN_CHAT_ID` — Telegram admin or group chat ID.
- `ADMIN_CHAT_IDS` — comma-separated admin IDs for multiple admins.
- `WA_LINK` — WhatsApp link.
- `GOOGLE_SHEET_ID` — Google Sheet ID from the URL.
- `GOOGLE_SHEET_NAME` — worksheet name, default: `Лиды`.
- `GOOGLE_SERVICE_ACCOUNT_JSON` — Google service account JSON as one line.

## Local Run

1. Copy `.env.example` to `.env`.
2. Fill in `BOT_TOKEN`.
3. Fill in `WA_LINK`.
4. Install dependencies: `pip install -r requirements.txt`.
5. Start the bot: `python bot.py`.
6. Send `/id` to the bot and put the returned `Chat ID` into `ADMIN_CHAT_ID`.
7. Restart the bot.

## Google Sheets

1. Create a Google Cloud project.
2. Enable Google Sheets API.
3. Create a Service Account and JSON key.
4. Create a Google Sheet.
5. Share the sheet with the service account email as Editor.
6. Set `GOOGLE_SERVICE_ACCOUNT_JSON` on the server.

## Hosting

Any host that can run a persistent Python process is suitable:

- Render Background Worker
- Railway
- VPS

Use:

```text
Build command: pip install -r requirements.txt
Start command: python bot.py
```
