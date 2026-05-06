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
from db import create_quiz_session, get_stats as get_db_stats, is_configured as is_db_configured, save_completed_lead


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
    file_exists = LEADS_PATH.exists() and LEADS_PATH.stat().st_size > 0
    if file_exists:
        with LEADS_PATH.open("r", newline="", encoding="utf-8") as f:
            first_row = next(csv.reader(f), [])
        file_exists = first_row == FIELDNAMES

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

    spreadsheet = _open_spreadsheet()

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
        save_completed_lead(user_data, user, row, SOURCE_TAG)
    except Exception:
        logger.exception("Failed to save lead to PostgreSQL")
    try:
        _save_to_google_sheet(row)
    except Exception:
        logger.exception("Failed to save lead to Google Sheets")
    return path


def start_quiz_session(user_data: dict, user) -> None:
    session_id = create_quiz_session(user, SOURCE_TAG)
    if session_id:
        user_data["db_session_id"] = session_id


def get_lead_stats() -> dict:
    if is_db_configured():
        try:
            return get_db_stats()
        except Exception:
            logger.exception("Failed to load lead stats from PostgreSQL")

    values = _get_google_sheet_values()
    if not values:
        return {
            "total": 0,
            "new": 0,
            "in_progress": 0,
            "no_answer": 0,
            "booked": 0,
            "refused": 0,
            "closed": 0,
            "conversion": 0,
            "avg_score": 0,
            "avg_energy": 0,
        }

    headers = values[0]
    rows = [row for row in values[1:] if row and row[0]]
    status_idx = headers.index("Статус") if "Статус" in headers else 2
    score_idx = headers.index("Балл") if "Балл" in headers else 12
    energy_idx = headers.index("Энергия, %") if "Энергия, %" in headers else 14

    def cell(row: list, idx: int) -> str:
        return row[idx] if idx < len(row) else ""

    total = len(rows)
    statuses = [cell(row, status_idx) for row in rows]
    booked = statuses.count("Записан на консультацию")
    scores = [_to_float(cell(row, score_idx)) for row in rows if cell(row, score_idx)]
    energies = [_to_float(cell(row, energy_idx)) for row in rows if cell(row, energy_idx)]

    return {
        "total": total,
        "new": statuses.count("Новая заявка"),
        "in_progress": statuses.count("В работе"),
        "no_answer": statuses.count("Не дозвонились"),
        "booked": booked,
        "refused": statuses.count("Отказ"),
        "closed": statuses.count("Закрыта"),
        "conversion": (booked / total * 100) if total else 0,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "avg_energy": sum(energies) / len(energies) if energies else 0,
    }


def _get_google_sheet_values() -> list:
    if not GOOGLE_SHEET_ID or not (GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE):
        return []

    spreadsheet = _open_spreadsheet()
    worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
    return worksheet.get_all_values()


def _open_spreadsheet():
    import gspread

    if GOOGLE_SERVICE_ACCOUNT_JSON:
        credentials = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    else:
        credentials = json.loads(Path(GOOGLE_SERVICE_ACCOUNT_FILE).read_text(encoding="utf-8"))

    client = gspread.service_account_from_dict(credentials)
    return client.open_by_key(GOOGLE_SHEET_ID)


def _to_float(value: str) -> float:
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return 0
