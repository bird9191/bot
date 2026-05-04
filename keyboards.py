from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import WA_LINK
from data import QUESTIONS


def kb_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Начать проверку →", callback_data="start_quiz")]]
    )


def kb_question(q_idx: int, multi_selected: list) -> InlineKeyboardMarkup:
    q = QUESTIONS[q_idx]
    rows = []
    for i, (label, _) in enumerate(q["opts"]):
        prefix = "✅ " if i in multi_selected else ""
        rows.append([InlineKeyboardButton(f"{prefix}{label}", callback_data=f"ans_{i}")])
    if q["multi"] and multi_selected:
        rows.append([InlineKeyboardButton("✅ Готово", callback_data="multi_done")])
    return InlineKeyboardMarkup(rows)


def kb_result(cta_label: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(cta_label, callback_data="get_plan")],
        [InlineKeyboardButton("Написать в WhatsApp", url=WA_LINK)],
    ])


def kb_contact_time() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Сейчас", callback_data="time_now"),
         InlineKeyboardButton("Сегодня", callback_data="time_today")],
        [InlineKeyboardButton("Завтра", callback_data="time_tomorrow"),
         InlineKeyboardButton("Написать в WhatsApp", callback_data="time_wa")],
    ])


def kb_whatsapp() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Открыть WhatsApp Clean Clinic", url=WA_LINK)]]
    )
