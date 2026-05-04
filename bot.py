import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from config import BOT_TOKEN, QUIZ, COLLECT_NAME, COLLECT_PHONE, COLLECT_CONCERN, COLLECT_TIME
from handlers.quiz import cmd_start, handle_start_quiz, handle_answer, cmd_cancel
from handlers.result import show_result
from handlers.form import handle_get_plan, collect_name, collect_phone, collect_concern, collect_time

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    await update.message.reply_text(
        f"Chat ID: {chat.id}\n"
        f"User ID: {user.id}\n\n"
        "Для уведомлений админу укажи Chat ID в ADMIN_CHAT_ID."
    )


def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
        raise RuntimeError("Set BOT_TOKEN in .env or environment variables before starting the bot.")

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            QUIZ: [
                CallbackQueryHandler(handle_start_quiz, pattern="^start_quiz$"),
                CallbackQueryHandler(handle_answer, pattern="^(ans_\\d+|multi_done)$"),
            ],
            COLLECT_NAME: [
                CallbackQueryHandler(handle_get_plan, pattern="^get_plan$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name),
            ],
            COLLECT_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone),
            ],
            COLLECT_CONCERN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_concern),
            ],
            COLLECT_TIME: [
                CallbackQueryHandler(collect_time, pattern="^time_"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("id", cmd_id))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
