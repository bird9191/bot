# Онлайн-заявки в Google Sheets

## Что получится

- Каждая заявка сохраняется локально в `leads.csv`.
- Если подключить Google Sheets, каждая заявка также появится в онлайн-таблице.
- Доступ администраторам выдается через кнопку `Share` в Google Sheets.
- Telegram-уведомления можно отправлять одному админу, нескольким админам или в общий чат.
- Вкладка `Лиды` работает как простая CRM: есть статус, ответственный, следующий контакт, результат звонка и комментарий администратора.

## Google Sheets

1. Создай Google-таблицу, например `Clean Clinic — заявки`.
2. Скопируй ID таблицы из URL:
   `https://docs.google.com/spreadsheets/d/<GOOGLE_SHEET_ID>/edit`
3. В Google Cloud включи `Google Sheets API`.
4. Создай `Service Account`.
5. Создай JSON-ключ для service account.
6. Открой созданный JSON и найди поле `client_email`.
7. В Google-таблице нажми `Share` и дай этому `client_email` доступ `Editor`.
8. Добавь администраторов в `Share` с доступом `Viewer` или `Editor`.

## Локальная настройка

В `.env` добавь:

```env
GOOGLE_SHEET_ID=ID_таблицы_из_URL
GOOGLE_SHEET_NAME=Лиды
GOOGLE_SERVICE_ACCOUNT_FILE=/полный/путь/к/service-account.json
```

Для сервера удобнее использовать переменную одной строкой:

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

## Несколько Telegram-админов

Можно указать один ID:

```env
ADMIN_CHAT_ID=5524476590
```

Или несколько через запятую:

```env
ADMIN_CHAT_IDS=5524476590,111111111,222222222
```

Если админы сидят в одной Telegram-группе, добавь бота в группу, напиши там `/id` и укажи ID группы в `ADMIN_CHAT_ID`.

## Запуск 24/7

Для настоящего онлайн-режима бот должен работать на сервере постоянно. Подойдут Railway, Render Background Worker или VPS. На сервере нужно задать те же переменные окружения, что в `.env`, но сам `.env` в GitHub не загружать.
