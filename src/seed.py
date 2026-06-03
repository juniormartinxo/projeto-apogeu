from __future__ import annotations

import json
from pathlib import Path

from src import db


SEED_PATH = Path("data/seed_questions.json")


def load_seed_questions(path: Path = SEED_PATH) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        questions = json.load(file)
    if not isinstance(questions, list):
        raise ValueError("seed_questions.json must contain a list of questions.")
    return questions


def seed_if_needed(force: bool = False) -> int:
    db.init_db()
    questions = load_seed_questions()
    if force or db.question_count() < len(questions):
        for question in questions:
            db.upsert_question(question)
    db.get_or_create_player()
    return len(questions)
