# Render Background Worker

## Важно

Render Background Worker работает 24/7, но у Render нет бесплатного плана для background workers. В `render.yaml` указан минимальный платный план `starter`.

## Что уже настроено

- `render.yaml` описывает Background Worker.
- Runtime: Python.
- Build Command: `pip install -r requirements.txt`.
- Start Command: `python bot.py`.
- Google Sheet ID уже прописан.
- Секреты не хранятся в `render.yaml`; Render попросит ввести их в Dashboard.

## Переменные окружения на Render

В Render нужно указать:

```env
BOT_TOKEN=новый_токен_бота
ADMIN_CHAT_ID=5524476590
WA_LINK=https://wa.me/77001234567
GOOGLE_SERVICE_ACCOUNT_JSON=JSON_SERVICE_ACCOUNT_ОДНОЙ_СТРОКОЙ
```

Если нужно несколько админов:

```env
ADMIN_CHAT_IDS=5524476590,111111111,222222222
```

## Как получить GOOGLE_SERVICE_ACCOUNT_JSON одной строкой

На локальном компьютере из папки проекта выполни:

```bash
python3 -c "import json; print(json.dumps(json.load(open('/Users/magomed199/Downloads/arcane-geode-495219-k3-bf2fd0ce1fcd.json'))))"
```

Скопируй весь вывод и вставь в Render как значение `GOOGLE_SERVICE_ACCOUNT_JSON`.

Не отправляй этот JSON в чат и не добавляй его в GitHub.

## Деплой через GitHub

1. Создай GitHub-репозиторий для папки `clean_clinic_bot`.
2. Загрузи туда файлы проекта.
3. В Render нажми `New` -> `Blueprint`.
4. Выбери GitHub-репозиторий.
5. Render прочитает `render.yaml`.
6. Введи секретные переменные, которые помечены `sync: false`.
7. Нажми `Apply`.

## Проверка

1. После успешного deploy открой Logs в Render.
2. Должна быть строка `Application started`.
3. Напиши боту `/start`.
4. Пройди тест и оставь заявку.
5. Проверь вкладку `Лиды` в Google Sheets.

## Локальный бот

После запуска на Render не держи локально `python bot.py`, иначе два процесса будут одновременно читать Telegram updates.
