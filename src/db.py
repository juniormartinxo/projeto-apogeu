from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from src.game_logic import DEFAULT_PLAYER_NAME, PHASE_ORDER, PLAYER_INITIAL_HP, PHASES, derive_level, now_iso


DB_PATH = Path(os.environ.get("APOGEU_DB_PATH", "data/apogeu.db"))


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS player_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL,
                xp INTEGER NOT NULL,
                level INTEGER NOT NULL,
                chemistry_elo INTEGER NOT NULL,
                current_phase TEXT NOT NULL,
                hp INTEGER NOT NULL DEFAULT 100,
                correct_streak INTEGER NOT NULL DEFAULT 0,
                wrong_streak INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                phase_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                skill_tag TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                stem TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                explanation TEXT NOT NULL,
                hints_json TEXT NOT NULL,
                wrong_feedback_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                selected_option TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                attempt_number INTEGER NOT NULL,
                hint_level INTEGER NOT NULL,
                damage_done INTEGER NOT NULL,
                damage_taken INTEGER NOT NULL,
                xp_gain INTEGER NOT NULL,
                elo_before INTEGER,
                elo_after INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                phase_id TEXT NOT NULL,
                skill_tag TEXT NOT NULL,
                error_type TEXT NOT NULL,
                enemy_name TEXT NOT NULL,
                weakness TEXT NOT NULL,
                selected_option TEXT NOT NULL,
                hint_received TEXT NOT NULL,
                status TEXT NOT NULL,
                review_due_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS battles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id TEXT NOT NULL,
                enemy_name TEXT NOT NULL,
                player_hp INTEGER NOT NULL,
                enemy_hp INTEGER NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT
            );

            CREATE TABLE IF NOT EXISTS phase_progress (
                phase_id TEXT PRIMARY KEY,
                unlocked INTEGER NOT NULL,
                completed INTEGER NOT NULL,
                best_score INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS weak_skills (
                skill_tag TEXT PRIMARY KEY,
                count INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        timestamp = now_iso()
        for phase_id in PHASE_ORDER:
            conn.execute(
                """
                INSERT OR IGNORE INTO phase_progress (phase_id, unlocked, completed, best_score, updated_at)
                VALUES (?, ?, 0, 0, ?)
                """,
                (phase_id, 1 if phase_id == "fase_1" else 0, timestamp),
            )


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def _decode_question(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["options"] = json.loads(data.pop("options_json"))
    data["hints"] = json.loads(data.pop("hints_json"))
    data["wrong_feedback"] = json.loads(data.pop("wrong_feedback_json"))
    return data


def get_or_create_player() -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM player_state WHERE id = 1").fetchone()
        if row:
            return dict(row)

        timestamp = now_iso()
        conn.execute(
            """
            INSERT INTO player_state (
                id, name, xp, level, chemistry_elo, current_phase, hp,
                correct_streak, wrong_streak, created_at, updated_at
            )
            VALUES (1, ?, 0, 1, 1000, 'fase_1', ?, 0, 0, ?, ?)
            """,
            (DEFAULT_PLAYER_NAME, PLAYER_INITIAL_HP, timestamp, timestamp),
        )
        return dict(conn.execute("SELECT * FROM player_state WHERE id = 1").fetchone())


def update_player(**fields: Any) -> dict[str, Any]:
    allowed = {
        "name",
        "xp",
        "level",
        "chemistry_elo",
        "current_phase",
        "hp",
        "correct_streak",
        "wrong_streak",
    }
    clean = {key: value for key, value in fields.items() if key in allowed}
    if "xp" in clean and "level" not in clean:
        clean["level"] = derive_level(int(clean["xp"]))
    clean["updated_at"] = now_iso()

    assignments = ", ".join(f"{key} = ?" for key in clean)
    values = list(clean.values())
    values.append(1)

    with connect() as conn:
        conn.execute(f"UPDATE player_state SET {assignments} WHERE id = ?", values)
        return dict(conn.execute("SELECT * FROM player_state WHERE id = 1").fetchone())


def question_count() -> int:
    with connect() as conn:
        return int(conn.execute("SELECT COUNT(*) AS count FROM questions").fetchone()["count"])


def upsert_question(question: dict[str, Any]) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO questions (
                id, phase_id, topic, skill_tag, difficulty, stem, options_json,
                correct_option, explanation, hints_json, wrong_feedback_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                phase_id = excluded.phase_id,
                topic = excluded.topic,
                skill_tag = excluded.skill_tag,
                difficulty = excluded.difficulty,
                stem = excluded.stem,
                options_json = excluded.options_json,
                correct_option = excluded.correct_option,
                explanation = excluded.explanation,
                hints_json = excluded.hints_json,
                wrong_feedback_json = excluded.wrong_feedback_json
            """,
            (
                question["id"],
                question["phase_id"],
                question["topic"],
                question["skill_tag"],
                int(question["difficulty"]),
                question["stem"],
                json.dumps(question["options"], ensure_ascii=False),
                question["correct_option"],
                question["explanation"],
                json.dumps(question["hints"], ensure_ascii=False),
                json.dumps(question["wrong_feedback"], ensure_ascii=False),
            ),
        )


def list_questions(phase_id: str | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM questions"
    params: tuple[Any, ...] = ()
    if phase_id:
        sql += " WHERE phase_id = ?"
        params = (phase_id,)
    sql += " ORDER BY difficulty, id"
    with connect() as conn:
        return [_decode_question(row) for row in conn.execute(sql, params).fetchall()]


def get_question(question_id: str) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
    if row is None:
        raise KeyError(f"Question not found: {question_id}")
    return _decode_question(row)


def get_phase_progress() -> dict[str, dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM phase_progress ORDER BY phase_id").fetchall()
    return {row["phase_id"]: dict(row) for row in rows}


def unlock_phase(phase_id: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE phase_progress SET unlocked = 1, updated_at = ? WHERE phase_id = ?",
            (now_iso(), phase_id),
        )


def complete_phase(phase_id: str, best_score: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE phase_progress
            SET completed = 1, best_score = MAX(best_score, ?), updated_at = ?
            WHERE phase_id = ?
            """,
            (best_score, now_iso(), phase_id),
        )


def start_battle_record(phase_id: str, player_hp: int, enemy_hp: int) -> int:
    phase = PHASES[phase_id]
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO battles (phase_id, enemy_name, player_hp, enemy_hp, status, started_at)
            VALUES (?, ?, ?, ?, 'ativo', ?)
            """,
            (phase_id, phase["enemy_name"], player_hp, enemy_hp, now_iso()),
        )
        return int(cursor.lastrowid)


def finish_battle_record(battle_id: int, status: str, player_hp: int, enemy_hp: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE battles
            SET status = ?, player_hp = ?, enemy_hp = ?, ended_at = ?
            WHERE id = ?
            """,
            (status, player_hp, enemy_hp, now_iso(), battle_id),
        )


def record_attempt(payload: dict[str, Any]) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO attempts (
                question_id, selected_option, is_correct, attempt_number, hint_level,
                damage_done, damage_taken, xp_gain, elo_before, elo_after, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["question_id"],
                payload["selected_option"],
                1 if payload["is_correct"] else 0,
                payload["attempt_number"],
                payload["hint_level"],
                payload["damage_done"],
                payload["damage_taken"],
                payload["xp_gain"],
                payload.get("elo_before"),
                payload.get("elo_after"),
                payload.get("created_at") or now_iso(),
            ),
        )


def record_error(payload: dict[str, Any]) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO errors (
                question_id, phase_id, skill_tag, error_type, enemy_name, weakness,
                selected_option, hint_received, status, review_due_at, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["question_id"],
                payload["phase_id"],
                payload["skill_tag"],
                payload["error_type"],
                payload["enemy_name"],
                payload["weakness"],
                payload["selected_option"],
                payload["hint_received"],
                payload["status"],
                payload["review_due_at"],
                payload["created_at"],
            ),
        )


def list_active_errors() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT e.*, q.topic, q.stem
            FROM errors e
            JOIN questions q ON q.id = e.question_id
            WHERE e.status = 'ativo'
            ORDER BY e.created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def resolve_error(error_id: int) -> None:
    with connect() as conn:
        conn.execute("UPDATE errors SET status = 'revisado' WHERE id = ?", (error_id,))


def get_skill_error_count(skill_tag: str) -> int:
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM errors WHERE skill_tag = ?",
            (skill_tag,),
        ).fetchone()
    return int(row["count"])


def get_recent_errors(limit: int = 8) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT skill_tag, error_type, created_at
            FROM errors
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def mark_weak_skill(skill_tag: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO weak_skills (skill_tag, count, updated_at)
            VALUES (?, 1, ?)
            ON CONFLICT(skill_tag) DO UPDATE SET
                count = count + 1,
                updated_at = excluded.updated_at
            """,
            (skill_tag, now_iso()),
        )


def list_attempts() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT a.*, q.skill_tag, q.topic
            FROM attempts a
            JOIN questions q ON q.id = a.question_id
            ORDER BY a.created_at DESC, a.id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def evolution_stats() -> dict[str, Any]:
    attempts = list_attempts()
    correct_by_skill: dict[str, int] = {}
    wrong_by_type: dict[str, int] = {}
    for attempt in attempts:
        if attempt["is_correct"]:
            correct_by_skill[attempt["skill_tag"]] = correct_by_skill.get(attempt["skill_tag"], 0) + 1
    for error in list_active_errors():
        wrong_by_type[error["error_type"]] = wrong_by_type.get(error["error_type"], 0) + 1
    return {
        "attempts": attempts,
        "correct_by_skill": correct_by_skill,
        "wrong_by_type": wrong_by_type,
        "active_errors": list_active_errors(),
    }
