from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import COLLECT_NAME, COLLECT_PHONE, COLLECT_CONCERN, COLLECT_TIME
from keyboards import kb_contact_time, kb_whatsapp
from admin import notify_admin
from storage import save_lead
from utils import html_escape


async def handle_get_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "*Как вас зовут?*\n\nВведите ваше имя:",
        parse_mode="MarkdownV2",
    )
    return COLLECT_NAME


async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Пожалуйста, введите корректное имя\\.", parse_mode="MarkdownV2")
        return COLLECT_NAME

    context.user_data["name"] = name
    await update.message.reply_text(
        f"Отлично, <b>{html_escape(name)}</b>! 👋\n\n"
        f"Укажите номер телефона — администратор отправит вам результат и предложит удобное время консультации:",
        parse_mode="HTML",
    )
    return COLLECT_PHONE


async def collect_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip()
    digits = "".join(c for c in raw if c.isdigit())
    if len(digits) < 10:
        await update.message.reply_text("Пожалуйста, введите корректный номер телефона\\.", parse_mode="MarkdownV2")
        return COLLECT_PHONE

    context.user_data["phone"] = raw
    await update.message.reply_text("Когда удобно связаться?", reply_markup=kb_contact_time())
    return COLLECT_TIME


async def collect_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    time_map = {
        "time_now": "Сейчас",
        "time_today": "Сегодня",
        "time_tomorrow": "Завтра",
        "time_wa": "Написать в WhatsApp",
    }
    context.user_data["time"] = time_map.get(query.data, "Не указано")

    await query.edit_message_text(
        "Что беспокоит больше всего? Напишите коротко \\(усталость, сон, стресс и т\\.д\\.\\):\n\n"
        "_Или напишите «—» чтобы пропустить_",
        parse_mode="MarkdownV2",
    )
    return COLLECT_CONCERN


async def collect_concern(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    concern = update.message.text.strip()
    context.user_data["concern"] = "" if concern == "—" else concern

    save_lead(context.user_data, update.effective_user)

    try:
        await notify_admin(context, update.effective_user)
    except Exception:
        context.application.logger.exception("Failed to notify admin")

    await update.message.reply_text(
        "✅ *Спасибо, заявка принята\\!*\n\n"
        "Мы передали ваши ответы администратору Clean Clinic\\.\n\n"
        "С вами свяжутся и подскажут, какие шаги лучше сделать дальше: "
        "консультация, анализы или восстановительная программа\\.",
        parse_mode="MarkdownV2",
        reply_markup=kb_whatsapp(),
    )
    return ConversationHandler.END
