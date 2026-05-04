# Онлайн-запуск Clean Clinic Bot

## Как будет работать

Бот запускается на сервере 24/7 через `python bot.py`.
QR можно вести прямо на ссылку Telegram-бота: `https://t.me/<username_бота>`.

Заявки сохраняются в Google Sheets, если заданы переменные `GOOGLE_SHEET_ID` и
`GOOGLE_SERVICE_ACCOUNT_JSON`. Локальный `leads.csv` остается запасной копией.

## Переменные окружения

Обязательные:

- `BOT_TOKEN` — токен бота от BotFather.

Желательные:

- `ADMIN_CHAT_ID` — Telegram ID администратора или группы для уведомлений.
- `WA_LINK` — ссылка WhatsApp, например `https://wa.me/77001234567`.
- `GOOGLE_SHEET_ID` — ID Google-таблицы из URL.
- `GOOGLE_SHEET_NAME` — название листа, по умолчанию `Лиды`.
- `GOOGLE_SERVICE_ACCOUNT_JSON` — JSON service account одной строкой.

## Локальный запуск

1. Скопируй `.env.example` в `.env`.
2. Вставь токен из BotFather в `BOT_TOKEN`.
3. Укажи ссылку WhatsApp в `WA_LINK`.
4. Установи зависимости: `pip install -r requirements.txt`.
5. Запусти бота: `python bot.py`.
6. Напиши боту `/id` и скопируй `Chat ID` в `ADMIN_CHAT_ID`.
7. Перезапусти бота, чтобы уведомления администратору начали приходить.

## Google Sheets

1. Создай Google Cloud project.
2. Включи Google Sheets API.
3. Создай Service Account и JSON key.
4. Создай Google Sheet.
5. Поделись таблицей с email service account с правом Editor.
6. На сервере добавь JSON ключ в `GOOGLE_SERVICE_ACCOUNT_JSON`.

## Railway

1. Залей проект в GitHub.
2. Создай Railway project из GitHub repo.
3. Start command: `python bot.py`.
4. Добавь переменные окружения.
5. Deploy.

## Render

Для Telegram polling нужен Background Worker.

1. Залей проект в GitHub.
2. Создай Background Worker.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `python bot.py`.
5. Добавь переменные окружения.
6. Deploy.
