# Google Sheets CRM

## Features

- Leads are saved to Google Sheets.
- A local `leads.csv` file is kept as a backup.
- Admin access is managed through Google Sheets sharing settings.
- Telegram notifications can be sent to one admin, multiple admins, or a shared admin group.
- The `Лиды` worksheet works as a simple CRM with status, assignee, next contact, call result, and admin comment columns.
- The `Статистика` worksheet shows lead KPIs.

## Google Sheets Setup

1. Create a Google Sheet.
2. Copy the Sheet ID from the URL:
   `https://docs.google.com/spreadsheets/d/<GOOGLE_SHEET_ID>/edit`
3. Enable Google Sheets API in Google Cloud.
4. Create a Service Account.
5. Create a JSON key for the Service Account.
6. Open the JSON key and copy `client_email`.
7. Share the Google Sheet with `client_email` as Editor.
8. Add admins to the Google Sheet as Viewer or Editor.

## Local Variables

```env
GOOGLE_SHEET_ID=sheet_id_from_url
GOOGLE_SHEET_NAME=Лиды
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service-account.json
```

## Server Variables

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

## Formatting

Apply CRM formatting and rebuild the statistics worksheet:

```bash
python format_sheet.py
```

## QR Code

The QR code points to:

```text
https://t.me/Tests2609bot
```

Regenerate the PNG file:

```bash
python generate_qr.py
```

## Admin IDs

Single admin:

```env
ADMIN_CHAT_ID=5524476590
```

Multiple admins:

```env
ADMIN_CHAT_IDS=5524476590,111111111,222222222
```

For a shared Telegram admin group, add the bot to the group, run `/id`, and use the group chat ID.
