from telegram import Update
from telegram.ext import ContextTypes
from config import COLLECT_NAME
from data import get_risk, get_causes
from keyboards import kb_result
from utils import html_escape


async def show_result(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    total = context.user_data.get("score", 0)
    answers = context.user_data.get("answers", [])
    risk = get_risk(total)
    causes = get_causes(answers)

    causes_text = "\n".join(f"• возможны признаки: {html_escape(c)}" for c in causes)

    text = (
        f"🏥 <b>Clean Clinic — Результат</b>\n\n"
        f"<b>Уровень энергии: {html_escape(risk['energy'])}%</b>\n"
        f"<i>{html_escape(risk['label'])}</i>\n\n"
        f"{html_escape(risk['text'])}\n\n"
        f"<b>Что может быть причиной:</b>\n{causes_text}\n\n"
        f"<b>Что делать дальше:</b>\n"
        f"В Clean Clinic врач может оценить твоё состояние, назначить необходимые "
        f"анализы и составить индивидуальный план восстановления.\n\n"
        f"<i>Это не диагноз. Точную причину может определить врач.</i>"
    )

    context.user_data["risk"] = risk
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb_result(risk["cta"]))
    return COLLECT_NAME
