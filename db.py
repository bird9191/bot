import json
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from config import DATABASE_URL
from data import QUESTIONS


logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(DATABASE_URL)


@contextmanager
def get_connection():
    import psycopg

    with psycopg.connect(DATABASE_URL) as conn:
        yield conn


def init_db() -> None:
    if not is_configured():
        return

    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.execute(schema)


def upsert_telegram_user(conn, user) -> int:
    row = conn.execute(
        """
        INSERT INTO telegram_users (
            telegram_id,
            username,
            first_name,
            last_name,
            language_code,
            is_bot
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            language_code = EXCLUDED.language_code,
            is_bot = EXCLUDED.is_bot,
            last_seen_at = now()
        RETURNING id
        """,
        (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.language_code,
            bool(user.is_bot),
        ),
    ).fetchone()
    return row[0]


def create_quiz_session(user, source: str) -> int | None:
    if not is_configured():
        return None

    try:
        with get_connection() as conn:
            user_id = upsert_telegram_user(conn, user)
            row = conn.execute(
                """
                INSERT INTO quiz_sessions (telegram_user_id, source)
                VALUES (%s, %s)
                RETURNING id
                """,
                (user_id, source),
            ).fetchone()
            return row[0]
    except Exception:
        logger.exception("Failed to create quiz session")
        return None


def save_completed_lead(user_data: dict, user, row: dict, source: str) -> None:
    if not is_configured():
        return

    with get_connection() as conn:
        user_id = upsert_telegram_user(conn, user)
        session_id = user_data.get("db_session_id")

        if session_id:
            conn.execute(
                """
                UPDATE quiz_sessions
                SET status = 'completed',
                    completed_at = now(),
                    score = %s,
                    risk_label = %s,
                    energy_percent = %s,
                    goal = %s
                WHERE id = %s AND telegram_user_id = %s
                """,
                (
                    _to_int(row.get("Балл")),
                    row.get("Уровень риска"),
                    _to_int(row.get("Энергия, %")),
                    row.get("Цель"),
                    session_id,
                    user_id,
                ),
            )
        else:
            session_id = conn.execute(
                """
                INSERT INTO quiz_sessions (
                    telegram_user_id,
                    source,
                    status,
                    completed_at,
                    score,
                    risk_label,
                    energy_percent,
                    goal
                )
                VALUES (%s, %s, 'completed', now(), %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    user_id,
                    source,
                    _to_int(row.get("Балл")),
                    row.get("Уровень риска"),
                    _to_int(row.get("Энергия, %")),
                    row.get("Цель"),
                ),
            ).fetchone()[0]

        for answer in user_data.get("answers", []):
            question = QUESTIONS[answer["q_idx"]]
            selected_options = [
                {"label": question["opts"][idx][0], "score": question["opts"][idx][1]}
                for idx in answer.get("sel", [])
            ]
            conn.execute(
                """
                INSERT INTO quiz_answers (
                    session_id,
                    question_index,
                    question_tag,
                    question_text,
                    selected_options,
                    score
                )
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                ON CONFLICT (session_id, question_index) DO UPDATE SET
                    selected_options = EXCLUDED.selected_options,
                    score = EXCLUDED.score,
                    answered_at = now()
                """,
                (
                    session_id,
                    answer["q_idx"],
                    question["tag"],
                    question["text"],
                    json.dumps(selected_options, ensure_ascii=False),
                    answer.get("score", 0),
                ),
            )

        conn.execute(
            """
            INSERT INTO leads (
                quiz_session_id,
                telegram_user_id,
                source,
                status,
                name,
                phone,
                contact_time,
                assigned_to,
                next_action,
                call_result,
                admin_comment,
                concern,
                score,
                risk_label,
                energy_percent,
                complaints,
                last_tests,
                goal,
                telegram_username,
                telegram_id
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                session_id,
                user_id,
                row.get("Источник"),
                row.get("Статус"),
                row.get("Имя"),
                row.get("Телефон"),
                row.get("Когда связаться"),
                row.get("Ответственный"),
                row.get("Следующий шаг"),
                row.get("Результат звонка"),
                row.get("Комментарий администратора"),
                row.get("Что беспокоит"),
                _to_int(row.get("Балл")),
                row.get("Уровень риска"),
                _to_int(row.get("Энергия, %")),
                row.get("Жалобы"),
                row.get("Последние анализы"),
                row.get("Цель"),
                row.get("Telegram username"),
                row.get("Telegram ID"),
            ),
        )


def get_stats() -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                count(*)::int AS total,
                count(*) FILTER (WHERE status = 'Новая заявка')::int AS new,
                count(*) FILTER (WHERE status = 'В работе')::int AS in_progress,
                count(*) FILTER (WHERE status = 'Не дозвонились')::int AS no_answer,
                count(*) FILTER (WHERE status = 'Записан на консультацию')::int AS booked,
                count(*) FILTER (WHERE status = 'Отказ')::int AS refused,
                count(*) FILTER (WHERE status = 'Закрыта')::int AS closed,
                coalesce(avg(score), 0)::float AS avg_score,
                coalesce(avg(energy_percent), 0)::float AS avg_energy
            FROM leads
            """
        ).fetchone()

    total = row[0]
    booked = row[4]
    return {
        "total": total,
        "new": row[1],
        "in_progress": row[2],
        "no_answer": row[3],
        "booked": booked,
        "refused": row[5],
        "closed": row[6],
        "conversion": (booked / total * 100) if total else 0,
        "avg_score": row[7],
        "avg_energy": row[8],
    }


def _to_int(value: Any) -> int:
    try:
        return int(float(str(value).replace(",", ".")))
    except (TypeError, ValueError):
        return 0
