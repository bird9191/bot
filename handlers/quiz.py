from telegram import Update
from telegram.helpers import escape_markdown
from telegram.ext import ContextTypes, ConversationHandler
from config import QUIZ, COLLECT_NAME
from data import QUESTIONS
from keyboards import kb_start, kb_question


def _question_text(q_idx: int) -> str:
    q = QUESTIONS[q_idx]
    total = len(QUESTIONS)
    bar = "▓" * (q_idx + 1) + "░" * (total - q_idx - 1)
    tag = escape_markdown(q["tag"], version=2)
    text = escape_markdown(q["text"], version=2)
    return f"*{tag}  •  Вопрос {q_idx + 1} из {total}*\n{bar}\n\n{text}"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data.update({"answers": [], "score": 0, "multi_sel": []})
    await update.message.reply_text(
        "🏥 *Clean Clinic*\n\n"
        "*Проверь уровень энергии за 60 секунд*\n\n"
        "Ответь на 10 коротких вопросов и получи персональный вывод: "
        "почему ты можешь чувствовать усталость, сонливость, стресс или упадок сил\\.\n\n"
        "_Это не медицинский диагноз\\. Результат поможет понять, стоит ли пройти консультацию врача\\._",
        parse_mode="MarkdownV2",
        reply_markup=kb_start(),
    )
    return QUIZ


async def handle_start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.update({"q_idx": 0, "multi_sel": []})
    await query.edit_message_text(
        _question_text(0),
        parse_mode="MarkdownV2",
        reply_markup=kb_question(0, []),
    )
    return QUIZ


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    q_idx = context.user_data.get("q_idx", 0)
    q = QUESTIONS[q_idx]

    if query.data == "multi_done":
        return await _finalize(query, context, q_idx)

    opt_idx = int(query.data.split("_")[1])

    if q["multi"]:
        sel = context.user_data["multi_sel"]
        is_exclusive = q["opts"][opt_idx][0] == "Ничего из этого"

        if is_exclusive:
            sel.clear()
            sel.append(opt_idx)
        else:
            exclusive = [i for i, (lbl, _) in enumerate(q["opts"]) if lbl == "Ничего из этого"]
            for ei in exclusive:
                if ei in sel:
                    sel.remove(ei)
            if opt_idx in sel:
                sel.remove(opt_idx)
            else:
                sel.append(opt_idx)

        context.user_data["multi_sel"] = sel
        await query.edit_message_reply_markup(reply_markup=kb_question(q_idx, sel))
        return QUIZ

    context.user_data["multi_sel"] = [opt_idx]
    return await _finalize(query, context, q_idx)


async def _finalize(query, context: ContextTypes.DEFAULT_TYPE, q_idx: int) -> int:
    from handlers.result import show_result

    q = QUESTIONS[q_idx]
    sel = context.user_data["multi_sel"]

    score = min(sum(q["opts"][i][1] for i in sel), 3) if q["multi"] else q["opts"][sel[0]][1]

    if q_idx == len(QUESTIONS) - 1:
        context.user_data["goal"] = q["opts"][sel[0]][0]

    context.user_data["answers"].append({
        "q_idx": q_idx,
        "sel": list(sel),
        "score": score,
        "labels": [q["opts"][i][0] for i in sel],
    })
    context.user_data["score"] = context.user_data.get("score", 0) + score
    context.user_data["multi_sel"] = []

    next_idx = q_idx + 1
    if next_idx < len(QUESTIONS):
        context.user_data["q_idx"] = next_idx
        await query.edit_message_text(
            _question_text(next_idx),
            parse_mode="MarkdownV2",
            reply_markup=kb_question(next_idx, []),
        )
        return QUIZ

    return await show_result(query, context)


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Тест прерван\\. Чтобы начать заново — /start", parse_mode="MarkdownV2")
    return ConversationHandler.END
