# Render Background Worker

## Service

`render.yaml` defines a Background Worker for the Telegram bot.

## Configuration

- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `python bot.py`
- Google Sheet ID is included in `render.yaml`
- Secrets are configured in the Render Dashboard

## Environment Variables

```env
BOT_TOKEN=telegram_bot_token
ADMIN_CHAT_ID=5524476590
WA_LINK=https://wa.me/77001234567
GOOGLE_SERVICE_ACCOUNT_JSON=service_account_json_as_one_line
```

Optional multiple admins:

```env
ADMIN_CHAT_IDS=5524476590,111111111,222222222
```

## GOOGLE_SERVICE_ACCOUNT_JSON

Convert the downloaded service account JSON file to one line:

```bash
python3 -c "import json; print(json.dumps(json.load(open('/path/to/service-account.json'))))"
```

Use the command output as the value of `GOOGLE_SERVICE_ACCOUNT_JSON`.

## Deploy

1. Push the project to GitHub.
2. In Render, create a new Blueprint.
3. Select the GitHub repository.
4. Render reads `render.yaml`.
5. Fill in variables marked with `sync: false`.
6. Apply the Blueprint.

## Check

1. Open Render logs.
2. Confirm `Application started`.
3. Send `/start` to the bot.
4. Complete the test and submit a lead.
5. Check the `Лиды` worksheet in Google Sheets.

After Render is running, stop any local `python bot.py` process to avoid duplicate polling.
