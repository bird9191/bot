import csv
import json
import logging
from datetime import datetime
from pathlib import Path

from config import (
    GOOGLE_SERVICE_ACCOUNT_FILE,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_NAME,
)


LEADS_PATH = Path(__file__).with_name("leads.csv")
SOURCE_TAG = "QR_BUS_TEST"
logger = logging.getLogger(__name__)

FIELDNAMES = [
    "Дата заявки",
    "Источник",
    "Статус",
    "Имя",
    "Телефон",
    "Когда связаться",
    "Ответственный",
    "Следующий шаг",
    "Следующий контакт",
    "Результат звонка",
    "Комментарий администратора",
    "Что беспокоит",
    "Балл",
    "Уровень риска",
    "Энергия, %",
    "Жалобы",
    "Последние анализы",
    "Цель",
    "Telegram username",
    "Telegram ID",
]


def _answer_labels(answers: list, idx: int) -> str:
    if len(answers) <= idx or not answers[idx].get("labels"):
        return "—"
    return ", ".join(answers[idx]["labels"])


def _build_row(user_data: dict, user) -> dict:
    answers = user_data.get("answers", [])
    risk = user_data.get("risk", {})
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "Дата заявки": created_at,
        "Источник": SOURCE_TAG,
        "Статус": "Новая заявка",
        "Имя": user_data.get("name", "—"),
        "Телефон": user_data.get("phone", "—"),
        "Когда связаться": user_data.get("time", "—"),
        "Ответственный": "",
        "Следующий шаг": "Позвонить / написать",
        "Следующий контакт": "",
        "Результат звонка": "",
        "Комментарий администратора": "",
        "Что беспокоит": user_data.get("concern") or "—",
        "Балл": user_data.get("score", 0),
        "Уровень риска": risk.get("label", "—"),
        "Энергия, %": risk.get("energy", "—"),
        "Жалобы": _answer_labels(answers, 2),
        "Последние анализы": _answer_labels(answers, 8),
        "Цель": user_data.get("goal", "—"),
        "Telegram username": user.username or "—",
        "Telegram ID": user.id,
    }


def _save_to_csv(row: dict) -> Path:
    file_exists = LEADS_PATH.exists()
    with LEADS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    return LEADS_PATH


def _save_to_google_sheet(row: dict) -> None:
    if not GOOGLE_SHEET_ID or not (GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE):
        return

    import gspread

    if GOOGLE_SERVICE_ACCOUNT_JSON:
        credentials = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    else:
        credentials = json.loads(Path(GOOGLE_SERVICE_ACCOUNT_FILE).read_text(encoding="utf-8"))

    client = gspread.service_account_from_dict(credentials)
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=GOOGLE_SHEET_NAME,
            rows=1000,
            cols=len(FIELDNAMES),
        )

    headers = worksheet.row_values(1)
    if not headers:
        worksheet.append_row(FIELDNAMES, value_input_option="USER_ENTERED")
    elif headers != FIELDNAMES:
        worksheet.update(
            range_name=f"A1:{_column_name(len(FIELDNAMES))}1",
            values=[FIELDNAMES],
            value_input_option="USER_ENTERED",
        )

    worksheet.append_row([row.get(field, "") for field in FIELDNAMES], value_input_option="USER_ENTERED")


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def save_lead(user_data: dict, user) -> Path:
    row = _build_row(user_data, user)
    path = _save_to_csv(row)
    try:
        _save_to_google_sheet(row)
    except Exception:
        logger.exception("Failed to save lead to Google Sheets")
    return path
