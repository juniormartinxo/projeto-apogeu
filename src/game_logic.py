from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from math import floor
from typing import Any


PLAYER_INITIAL_HP = 100
DEFAULT_PLAYER_NAME = "Cadete Apogeu"

PHASE_ORDER = ["fase_1", "fase_2", "fase_3"]

PHASES: dict[str, dict[str, Any]] = {
    "fase_1": {
        "id": "fase_1",
        "name": "Fundicao dos Mols",
        "title": "Fase 1 - Fundicao dos Mols",
        "topic": "Mol, massa molar e conversoes",
        "objective": "Acertar questoes basicas e medias para abrir a camara estequiometrica.",
        "enemy_name": "Molock - Vigia da Fundicao",
        "enemy_hp": 80,
        "unlock_next": "fase_2",
    },
    "fase_2": {
        "id": "fase_2",
        "name": "Camara do Reagente Limitante",
        "title": "Fase 2 - Camara do Reagente Limitante",
        "topic": "Estequiometria, limitante e rendimento",
        "objective": "Identificar quem acaba primeiro e calcular produto formado.",
        "enemy_name": "Molock - Executor de Proporcoes",
        "enemy_hp": 110,
        "unlock_next": "fase_3",
    },
    "fase_3": {
        "id": "fase_3",
        "name": "Molock, o Senhor dos Mols",
        "title": "Boss - Molock, o Senhor dos Mols",
        "topic": "Mistura de mol, estequiometria, limitante e rendimento",
        "objective": "Derrotar Molock em uma batalha final de Quimica Quantitativa.",
        "enemy_name": "Molock, o Senhor dos Mols",
        "enemy_hp": 160,
        "unlock_next": None,
    },
}

ERROR_ENEMY_BY_SKILL = {
    "massa_para_mol": "Golem da Massa Molar",
    "mol_para_massa": "Golem da Massa Molar",
    "massa_molar_composta": "Golem da Massa Molar",
    "mistura_mols": "Fantasma da Unidade",
    "proporcao_estequiometrica": "Espectro da Proporcao",
    "reagente_limitante": "Sombra do Reagente Limitante",
    "rendimento": "Parasita da Pressa",
}

WEAKNESS_BY_SKILL = {
    "massa_para_mol": "Usar n = m/M antes de comparar quantidades.",
    "mol_para_massa": "Converter mol para massa com m = n x M.",
    "massa_molar_composta": "Somar cada atomo da formula antes de dividir.",
    "mistura_mols": "Tratar cada substancia separadamente e somar apenas mols.",
    "proporcao_estequiometrica": "Comparar coeficientes em mol, nunca em grama.",
    "reagente_limitante": "Converter massa para mol antes de comparar proporcoes.",
    "rendimento": "Calcular o valor teorico antes de aplicar o percentual.",
}

ERROR_TYPE_BY_SKILL = {
    "massa_para_mol": "unidade",
    "mol_para_massa": "formula",
    "massa_molar_composta": "conceito",
    "mistura_mols": "unidade",
    "proporcao_estequiometrica": "proporção",
    "reagente_limitante": "proporção",
    "rendimento": "formula",
}

ERROR_KEYWORDS = {
    "unidade": ["grama", "massa", "mol", "unidade"],
    "conceito": ["conceito", "massa molar", "formula"],
    "proporção": ["proporcao", "proporção", "coeficiente", "limitante", "estequiometr"],
    "conta": ["divisao", "multiplic", "calculo", "conta"],
    "interpretacao": ["interpret", "enunciado"],
    "formula": ["rendimento", "percentual", "formula"],
    "pressa": ["pressa", "ordem"],
}

BOSS_TAUNTS = {
    "correct": [
        "Molock: Um impacto limpo. Ainda insuficiente.",
        "Molock: Voce calculou antes de correr. Raro.",
        "Molock: Acerto registrado. A pressao sobe.",
    ],
    "wrong": [
        "Molock: Voce trouxe gramas para uma guerra de mols. Pessima ideia.",
        "Molock: Pressa detectada. Vou aumentar a pressao.",
        "Molock: Voce sabe fazer conta. So esqueceu de pensar antes.",
    ],
    "proporcao": [
        "Molock: Errou proporcao de novo. Esse buraco esta virando endereco.",
        "Molock: Coeficiente ignorado. Ataque direto.",
    ],
    "proporção": [
        "Molock: Errou proporcao de novo. Esse buraco esta virando endereco.",
        "Molock: Coeficiente ignorado. Ataque direto.",
    ],
    "unidade": [
        "Molock: Unidade quebrada. Defesa aberta.",
        "Molock: Grama nao substitui mol. Impacto confirmado.",
    ],
    "formula": [
        "Molock: Formula usada sem controle. Previsivel.",
        "Molock: Percentual antes do teorico. Falha comum.",
    ],
    "pressa": [
        "Molock: Pressa detectada. Vou aumentar a pressao.",
        "Molock: Acelerou antes de pensar. Otimo para mim.",
    ],
}


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def review_due_iso(hours: int = 24) -> str:
    return (datetime.now() + timedelta(hours=hours)).replace(microsecond=0).isoformat(sep=" ")


def derive_level(total_xp: int) -> int:
    return 1 + floor(max(0, total_xp) / 250)


def calculate_player_damage(
    difficulty: int,
    streak: int,
    answered_seconds: float,
    hint_level: int,
    wrong_attempts: int,
) -> int:
    speed_bonus = 6 if answered_seconds < 60 else 0
    hint_penalty = 5 * max(0, hint_level)
    attempt_penalty = 8 * max(0, wrong_attempts)
    damage = 18 + 7 * difficulty + 3 * max(0, streak) + speed_bonus - hint_penalty - attempt_penalty
    return max(5, int(damage))


def calculate_boss_damage(difficulty: int, previous_skill_errors: int) -> int:
    if previous_skill_errors >= 3:
        repeated_error_penalty = 10
    elif previous_skill_errors >= 1:
        repeated_error_penalty = 5
    else:
        repeated_error_penalty = 0
    return max(5, 10 + 5 * difficulty + repeated_error_penalty)


def calculate_xp_gain(
    difficulty: int,
    first_try: bool,
    hint_level: int,
    phase_bonus: int = 0,
    final_boss_bonus: int = 0,
) -> int:
    question_xp = 10 + 5 * difficulty
    if first_try:
        question_xp += 20
    if hint_level == 0:
        question_xp += 10
    question_xp = max(0, question_xp - 5 * max(0, hint_level))
    return question_xp + max(0, phase_bonus) + max(0, final_boss_bonus)


def calculate_question_elo(player_elo: int, difficulty: int, is_correct: bool) -> int:
    question_rating = 850 + difficulty * 120
    expected = 1 / (1 + 10 ** ((question_rating - player_elo) / 400))
    score = 1 if is_correct else 0
    return round(player_elo + 24 * (score - expected))


def phase_bonus_for_victory(phase_id: str) -> tuple[int, int]:
    if phase_id == "fase_3":
        return 30, 80
    return 30, 0


def next_phase_id(phase_id: str) -> str | None:
    return PHASES.get(phase_id, {}).get("unlock_next")


def infer_error_type(question: dict[str, Any], selected_option: str | None) -> str:
    skill_tag = question.get("skill_tag", "")
    feedback = ""
    wrong_feedback = question.get("wrong_feedback") or {}
    if selected_option and selected_option in wrong_feedback:
        feedback = str(wrong_feedback[selected_option]).lower()

    for error_type, keywords in ERROR_KEYWORDS.items():
        if any(keyword in feedback for keyword in keywords):
            return error_type

    return ERROR_TYPE_BY_SKILL.get(skill_tag, "conceito")


def error_enemy_name(skill_tag: str, error_type: str | None = None) -> str:
    if skill_tag in ERROR_ENEMY_BY_SKILL:
        return ERROR_ENEMY_BY_SKILL[skill_tag]
    if error_type == "unidade":
        return "Fantasma da Unidade"
    if error_type in {"proporcao", "proporção"}:
        return "Espectro da Proporcao"
    if error_type == "pressa":
        return "Parasita da Pressa"
    return "Golem da Massa Molar"


def skill_weakness(skill_tag: str) -> str:
    return WEAKNESS_BY_SKILL.get(skill_tag, "Revisar a ordem de raciocinio antes de calcular.")


def build_error_payload(
    question: dict[str, Any],
    selected_option: str,
    hint_received: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    error_type = infer_error_type(question, selected_option)
    skill_tag = question["skill_tag"]
    return {
        "question_id": question["id"],
        "phase_id": question["phase_id"],
        "skill_tag": skill_tag,
        "error_type": error_type,
        "enemy_name": error_enemy_name(skill_tag, error_type),
        "weakness": skill_weakness(skill_tag),
        "selected_option": selected_option,
        "hint_received": hint_received,
        "status": "ativo",
        "review_due_at": review_due_iso(),
        "created_at": created_at or now_iso(),
    }


def choose_next_question(
    questions: list[dict[str, Any]],
    asked_question_ids: list[str],
    recent_errors: list[dict[str, Any]],
    correct_streak: int,
    wrong_streak: int,
    current_difficulty: int,
) -> dict[str, Any]:
    if not questions:
        raise ValueError("No questions available for this phase.")

    available = [q for q in questions if q["id"] not in set(asked_question_ids)]
    if not available:
        available = list(questions)

    target_difficulty = current_difficulty
    if correct_streak >= 3:
        target_difficulty = min(5, current_difficulty + 1)
    elif wrong_streak >= 3:
        target_difficulty = max(1, current_difficulty - 1)

    skill_counts = Counter(error.get("skill_tag") for error in recent_errors if error.get("skill_tag"))
    weak_skill = None
    if skill_counts:
        skill, count = skill_counts.most_common(1)[0]
        if count >= 2:
            weak_skill = skill

    candidates = available
    if weak_skill:
        skill_candidates = [q for q in available if q.get("skill_tag") == weak_skill]
        if skill_candidates:
            candidates = skill_candidates

    return sorted(
        candidates,
        key=lambda q: (
            abs(int(q.get("difficulty", 1)) - target_difficulty),
            int(q.get("difficulty", 1)),
            str(q.get("id", "")),
        ),
    )[0]


def build_mentor_context(
    question: dict[str, Any],
    selected_option: str | None,
    error_type: str | None,
    hint_level: int,
    skill_error_count: int,
) -> dict[str, Any]:
    hints = question.get("hints") or {}
    safe_level = max(0, min(5, hint_level))
    allowed_hint = hints.get(str(safe_level), "") if safe_level > 0 else ""
    return {
        "topic": question.get("topic"),
        "difficulty": question.get("difficulty"),
        "skill_tag": question.get("skill_tag"),
        "selected_option": selected_option or "nao selecionada",
        "error_type": error_type or "nao identificado",
        "hint_level": safe_level,
        "allowed_hint": allowed_hint,
        "same_skill_recent_errors": max(0, skill_error_count),
    }


def build_boss_context(
    phase_id: str,
    event: str,
    error_type: str | None,
    skill_tag: str | None,
    correct_streak: int,
    wrong_streak: int,
) -> dict[str, Any]:
    phase = PHASES.get(phase_id, PHASES["fase_1"])
    return {
        "boss_name": phase["enemy_name"],
        "event": event,
        "error_type": error_type or "nenhum",
        "skill_tag": skill_tag or "nenhum",
        "correct_streak": correct_streak,
        "wrong_streak": wrong_streak,
    }


def fallback_boss_taunt(context: dict[str, Any]) -> str:
    event = context.get("event", "wrong")
    error_type = context.get("error_type")
    pool = BOSS_TAUNTS.get(error_type) or BOSS_TAUNTS.get(event) or BOSS_TAUNTS["wrong"]
    index = (int(context.get("correct_streak", 0)) + int(context.get("wrong_streak", 0))) % len(pool)
    return pool[index]


def summarize_phase_status(progress: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    cards = []
    for phase_id in PHASE_ORDER:
        phase = PHASES[phase_id]
        state = progress.get(phase_id, {})
        cards.append(
            {
                **phase,
                "unlocked": bool(state.get("unlocked")),
                "completed": bool(state.get("completed")),
                "best_score": int(state.get("best_score") or 0),
            }
        )
    return cards
