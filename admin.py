from datetime import datetime
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_IDS
from storage import SOURCE_TAG
from utils import html_escape


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, user) -> None:
    if not ADMIN_CHAT_IDS:
        return

    ud = context.user_data
    risk = ud.get("risk", {})
    answers = ud.get("answers", [])
    score = ud.get("score", 0)

    last_tests = answers[8]["labels"][0] if len(answers) >= 9 and answers[8]["labels"] else "—"
    complaints = ", ".join(answers[2]["labels"]) if len(answers) >= 3 and answers[2]["labels"] else "—"

    text = (
        f"🔔 <b>Новая заявка — QR_BUS_TEST</b>\n\n"
        f"👤 <b>Имя:</b> {html_escape(ud.get('name', '—'))}\n"
        f"📱 <b>Телефон:</b> {html_escape(ud.get('phone', '—'))}\n"
        f"🕐 <b>Связаться:</b> {html_escape(ud.get('time', '—'))}\n"
        f"📍 <b>Источник:</b> QR автобус / наружная реклама\n"
        f"📅 <b>Дата:</b> {html_escape(datetime.now().strftime('%d.%m.%Y %H:%M'))}\n\n"
        f"📊 <b>Результат теста:</b>\n"
        f"• Балл: {score}/30\n"
        f"• Уровень риска: {html_escape(risk.get('label', '—'))}\n"
        f"• Энергия: {html_escape(risk.get('energy', '—'))}%\n\n"
        f"🩺 <b>Жалобы:</b> {html_escape(complaints)}\n"
        f"📋 <b>Последние анализы:</b> {html_escape(last_tests)}\n"
        f"🎯 <b>Цель:</b> {html_escape(ud.get('goal', '—'))}\n"
        f"💬 <b>Доп. информация:</b> {html_escape(ud.get('concern') or '—')}\n\n"
        f"👤 <b>Telegram:</b> @{html_escape(user.username or '—')} (ID: <code>{html_escape(user.id)}</code>)\n"
        f"🏷 <b>Тег:</b> {SOURCE_TAG}\n\n"
        f"📞 <b>Скрипт первого звонка:</b>\n"
        f"<i>«Здравствуйте, меня зовут ___, Clean Clinic. Вы прошли тест "
        f"\"Проверь себя\" по QR-коду. У вас в ответах отразились признаки "
        f"{html_escape(risk.get('label', 'снижения энергии').lower())}. Удобно сейчас 1 минуту?»</i>"
    )

    for chat_id in ADMIN_CHAT_IDS:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
        )
