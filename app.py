from __future__ import annotations

import time
from typing import Any

import pandas as pd
import streamlit as st

from src import db
from src.game_logic import (
    PHASES,
    PLAYER_INITIAL_HP,
    build_boss_context,
    build_error_payload,
    build_mentor_context,
    calculate_boss_damage,
    calculate_player_damage,
    calculate_question_elo,
    calculate_xp_gain,
    choose_next_question,
    infer_error_type,
    next_phase_id,
    phase_bonus_for_victory,
    summarize_phase_status,
)
from src.ollama_client import get_boss_taunt, get_mentor_hint
from src.seed import seed_if_needed
from src.ui_components import (
    battle_arena_header,
    boss_line,
    boss_svg,
    combat_question,
    enemy_dossier,
    hp_bar,
    inject_css,
    mentor_panel,
    mission_briefing,
    phase_card,
    pilot_hud,
    stat_card,
    tactical_logo,
)


def bootstrap() -> None:
    st.set_page_config(
        page_title="Protocolo Apogeu",
        page_icon="PA",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    seed_if_needed()
    inject_css()
    st.session_state.setdefault("view", "home")


def go(view: str) -> None:
    st.session_state["view"] = view
    st.rerun()


def current_player() -> dict[str, Any]:
    return db.get_or_create_player()


def start_battle(phase_id: str) -> None:
    phase = PHASES[phase_id]
    battle_id = db.start_battle_record(phase_id, PLAYER_INITIAL_HP, phase["enemy_hp"])
    db.update_player(hp=PLAYER_INITIAL_HP, current_phase=phase_id)
    st.session_state["battle"] = {
        "battle_id": battle_id,
        "phase_id": phase_id,
        "player_hp": PLAYER_INITIAL_HP,
        "enemy_hp": phase["enemy_hp"],
        "enemy_total_hp": phase["enemy_hp"],
        "asked_question_ids": [],
        "current_question_id": None,
        "current_difficulty": 1,
        "question_started_at": time.time(),
        "question_wrong_attempts": 0,
        "hint_level": 0,
        "mentor_text": "Vetor: Aguardando sua primeira decisão.",
        "boss_text": "Molock: Entre. A forja nao espera.",
        "history": [],
        "correct_streak": 0,
        "wrong_streak": 0,
        "status": "ativo",
        "last_result": None,
    }
    assign_next_question()
    st.session_state["view"] = "battle"
    st.rerun()


def assign_next_question() -> None:
    battle = st.session_state["battle"]
    questions = db.list_questions(battle["phase_id"])
    question = choose_next_question(
        questions=questions,
        asked_question_ids=battle["asked_question_ids"],
        recent_errors=db.get_recent_errors(),
        correct_streak=battle["correct_streak"],
        wrong_streak=battle["wrong_streak"],
        current_difficulty=battle["current_difficulty"],
    )
    battle["current_question_id"] = question["id"]
    battle["current_difficulty"] = int(question["difficulty"])
    battle["question_started_at"] = time.time()
    battle["question_wrong_attempts"] = 0
    battle["hint_level"] = 0
    battle["last_result"] = None
    battle["mentor_text"] = "Vetor: Observe a unidade antes de atacar."


def append_history(text: str) -> None:
    battle = st.session_state["battle"]
    battle["history"].insert(0, text)
    battle["history"] = battle["history"][:8]


def request_hint(question: dict[str, Any], selected_option: str | None) -> None:
    battle = st.session_state["battle"]
    hint_level = min(5, int(battle["hint_level"]) + 1)
    battle["hint_level"] = hint_level
    if hint_level >= 4:
        db.mark_weak_skill(question["skill_tag"])

    error_type = infer_error_type(question, selected_option)
    context = build_mentor_context(
        question=question,
        selected_option=selected_option,
        error_type=error_type,
        hint_level=hint_level,
        skill_error_count=db.get_skill_error_count(question["skill_tag"]),
    )
    battle["mentor_text"] = get_mentor_hint(context)
    append_history(f"Dica nivel {hint_level} solicitada em {question['skill_tag']}.")
    st.rerun()


def answer_question(question: dict[str, Any], selected_option: str) -> None:
    battle = st.session_state["battle"]
    player = current_player()
    is_correct = selected_option == question["correct_option"]
    attempt_number = int(battle["question_wrong_attempts"]) + 1
    elapsed = time.time() - float(battle["question_started_at"])
    elo_before = int(player["chemistry_elo"])
    elo_after = calculate_question_elo(elo_before, int(question["difficulty"]), is_correct)
    damage_done = 0
    damage_taken = 0
    xp_gain = 0
    phase_won = False
    battle_lost = False
    error_type = None

    if is_correct:
        damage_done = calculate_player_damage(
            difficulty=int(question["difficulty"]),
            streak=int(battle["correct_streak"]),
            answered_seconds=elapsed,
            hint_level=int(battle["hint_level"]),
            wrong_attempts=int(battle["question_wrong_attempts"]),
        )
        battle["enemy_hp"] = max(0, int(battle["enemy_hp"]) - damage_done)
        phase_won = battle["enemy_hp"] <= 0
        phase_bonus, final_bonus = phase_bonus_for_victory(battle["phase_id"]) if phase_won else (0, 0)
        xp_gain = calculate_xp_gain(
            difficulty=int(question["difficulty"]),
            first_try=attempt_number == 1,
            hint_level=int(battle["hint_level"]),
            phase_bonus=phase_bonus,
            final_boss_bonus=final_bonus,
        )
        new_xp = int(player["xp"]) + xp_gain
        battle["correct_streak"] = int(battle["correct_streak"]) + 1
        battle["wrong_streak"] = 0
        db.update_player(
            xp=new_xp,
            chemistry_elo=elo_after,
            correct_streak=battle["correct_streak"],
            wrong_streak=0,
            hp=battle["player_hp"],
        )
        battle["asked_question_ids"].append(question["id"])
        battle["boss_text"] = get_boss_taunt(
            build_boss_context(
                battle["phase_id"],
                "correct",
                None,
                question["skill_tag"],
                battle["correct_streak"],
                battle["wrong_streak"],
            )
        )
        battle["mentor_text"] = "Vetor: Questao encerrada. Agora leia a explicacao e avance."
        append_history(f"Acerto em {question['id']}: {damage_done} de dano, {xp_gain} XP.")

        if phase_won:
            score = max(0, battle["player_hp"]) + xp_gain
            db.complete_phase(battle["phase_id"], score)
            unlocked = next_phase_id(battle["phase_id"])
            if unlocked:
                db.unlock_phase(unlocked)
                db.update_player(current_phase=unlocked)
            db.finish_battle_record(
                battle["battle_id"],
                "vencida",
                battle["player_hp"],
                battle["enemy_hp"],
            )
            battle["status"] = "vencida"
    else:
        error_type = infer_error_type(question, selected_option)
        previous_skill_errors = db.get_skill_error_count(question["skill_tag"])
        damage_taken = calculate_boss_damage(int(question["difficulty"]), previous_skill_errors)
        battle["player_hp"] = max(0, int(battle["player_hp"]) - damage_taken)
        battle["wrong_streak"] = int(battle["wrong_streak"]) + 1
        battle["correct_streak"] = 0
        battle["question_wrong_attempts"] = attempt_number
        battle["hint_level"] = min(5, max(1, int(battle["hint_level"]) + 1))

        context = build_mentor_context(
            question=question,
            selected_option=selected_option,
            error_type=error_type,
            hint_level=int(battle["hint_level"]),
            skill_error_count=previous_skill_errors,
        )
        mentor_text = get_mentor_hint(context)
        battle["mentor_text"] = mentor_text
        if battle["hint_level"] >= 4:
            db.mark_weak_skill(question["skill_tag"])

        error_payload = build_error_payload(question, selected_option, mentor_text)
        db.record_error(error_payload)
        battle["boss_text"] = get_boss_taunt(
            build_boss_context(
                battle["phase_id"],
                "wrong",
                error_type,
                question["skill_tag"],
                battle["correct_streak"],
                battle["wrong_streak"],
            )
        )
        db.update_player(
            chemistry_elo=elo_after,
            hp=battle["player_hp"],
            correct_streak=0,
            wrong_streak=battle["wrong_streak"],
        )
        append_history(f"Erro em {question['id']}: Molock causou {damage_taken} de dano.")

        if battle["player_hp"] <= 0:
            battle_lost = True
            battle["status"] = "derrotada"
            db.finish_battle_record(
                battle["battle_id"],
                "derrotada",
                battle["player_hp"],
                battle["enemy_hp"],
            )

    db.record_attempt(
        {
            "question_id": question["id"],
            "selected_option": selected_option,
            "is_correct": is_correct,
            "attempt_number": attempt_number,
            "hint_level": battle["hint_level"],
            "damage_done": damage_done,
            "damage_taken": damage_taken,
            "xp_gain": xp_gain,
            "elo_before": elo_before,
            "elo_after": elo_after,
        }
    )

    battle["last_result"] = {
        "question_id": question["id"],
        "is_correct": is_correct,
        "selected_option": selected_option,
        "damage_done": damage_done,
        "damage_taken": damage_taken,
        "xp_gain": xp_gain,
        "elo_before": elo_before,
        "elo_after": elo_after,
        "explanation": question["explanation"] if is_correct or battle_lost else None,
        "wrong_feedback": (question.get("wrong_feedback") or {}).get(selected_option),
        "phase_won": phase_won,
        "battle_lost": battle_lost,
        "error_type": error_type,
    }
    st.rerun()


def render_top_nav() -> None:
    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        if st.button("Comando", key="nav_dashboard", use_container_width=True):
            go("home")
    with cols[1]:
        if st.button("Mapa", key="nav_campaign", use_container_width=True):
            go("campaign")
    with cols[2]:
        if st.button("Caderno de Erros", key="nav_errors", use_container_width=True):
            go("errors")
    with cols[3]:
        if st.button("Painel de Evolucao", key="nav_evolution", use_container_width=True):
            go("evolution")


def render_home() -> None:
    player = current_player()
    progress = db.get_phase_progress()
    current_phase = PHASES[player["current_phase"]]
    completed = sum(1 for item in progress.values() if item["completed"])

    tactical_logo()
    render_top_nav()

    pilot_hud(player, completed, current_phase["name"])
    mission_briefing(current_phase, completed)

    identity_cols = st.columns([0.72, 0.28])
    with identity_cols[0]:
        name = st.text_input("Identificação do cadete", value=player["name"], max_chars=40)
    with identity_cols[1]:
        st.write("")
        if st.button("Atualizar ID", key="home_update_name", use_container_width=True):
            db.update_player(name=name.strip() or player["name"])
            st.rerun()

    actions = st.columns(3)
    with actions[0]:
        if st.button("Entrar na campanha", key="home_continue_campaign", use_container_width=True):
            go("campaign")
    with actions[1]:
        if st.button("Caderno de Erros", key="home_errors", use_container_width=True):
            go("errors")
    with actions[2]:
        if st.button("Painel de Evolucao", key="home_evolution", use_container_width=True):
            go("evolution")


def render_campaign() -> None:
    tactical_logo()
    render_top_nav()
    st.markdown("### Mapa operacional")
    cards = summarize_phase_status(db.get_phase_progress())
    cols = st.columns(3)
    for col, phase in zip(cols, cards):
        with col:
            phase_card(phase)
            label = "Entrar" if not phase["completed"] else "Repetir batalha"
            if st.button(label, key=f"enter_{phase['id']}", disabled=not phase["unlocked"], use_container_width=True):
                start_battle(phase["id"])


def render_result_panel(question: dict[str, Any]) -> None:
    battle = st.session_state["battle"]
    result = battle.get("last_result")
    if not result or result["question_id"] != question["id"]:
        return

    if result["is_correct"]:
        st.success(
            f"Acerto confirmado. Dano: {result['damage_done']} | XP: {result['xp_gain']} | "
            f"ELO: {result['elo_before']} -> {result['elo_after']}"
        )
        st.markdown("**Explicacao tática liberada:**")
        st.info(result["explanation"])
    else:
        st.error(
            f"Resposta incorreta. Dano recebido: {result['damage_taken']} | "
            f"ELO: {result['elo_before']} -> {result['elo_after']}"
        )
        if result.get("wrong_feedback"):
            st.warning(result["wrong_feedback"])
        st.caption("A explicacao completa permanece bloqueada enquanto a tentativa estiver ativa.")


def render_battle() -> None:
    if "battle" not in st.session_state:
        start_battle(current_player()["current_phase"])
        return

    battle = st.session_state["battle"]
    phase = PHASES[battle["phase_id"]]
    question = db.get_question(battle["current_question_id"])
    result = battle.get("last_result")
    question_locked = bool(result and result["question_id"] == question["id"] and result["is_correct"])
    battle_finished = battle["status"] in {"vencida", "derrotada"}

    tactical_logo()
    render_top_nav()
    battle_arena_header(phase)

    hp_cols = st.columns(2)
    with hp_cols[0]:
        hp_bar("HP do jogador", battle["player_hp"], PLAYER_INITIAL_HP, player=True)
    with hp_cols[1]:
        hp_bar("HP do inimigo", battle["enemy_hp"], battle["enemy_total_hp"], player=False)

    left, right = st.columns([1.35, 0.85])
    with right:
        enemy_dossier(phase)
        boss_svg()
        boss_line(battle["boss_text"])
        mentor_panel(battle["mentor_text"])
        if battle["history"]:
            st.markdown("#### Log de combate")
            st.markdown("<div class='battle-history'>", unsafe_allow_html=True)
            for item in battle["history"]:
                st.markdown(f"<div class='history-line'>{item}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with left:
        if battle_finished:
            if battle["status"] == "vencida":
                st.success("Fase vencida. Protocolo atualizado.")
                if battle["phase_id"] == "fase_3":
                    st.info("Molock foi derrotado. MVP finalizado.")
                if st.button("Voltar ao mapa", key="battle_back_to_campaign", use_container_width=True):
                    st.session_state.pop("battle", None)
                    go("campaign")
            else:
                st.error("Batalha perdida. Revisao obrigatoria ativada.")
                st.write("Abra o caderno de erros e elimine os inimigos ativos antes de tentar novamente.")
                if st.button("Abrir caderno de erros", key="battle_open_errors_after_loss", use_container_width=True):
                    st.session_state.pop("battle", None)
                    go("errors")
            render_result_panel(question)
            return

        combat_question(question)
        render_result_panel(question)

        if question_locked:
            if st.button("Avancar para proxima questao", key=f"battle_advance_{question['id']}", use_container_width=True):
                assign_next_question()
                st.rerun()
            return

        options = question["options"]
        radio_key = f"option_{question['id']}_{battle['question_wrong_attempts']}"
        selected = st.radio(
            "Alternativas",
            list(options.keys()),
            index=None,
            key=radio_key,
            format_func=lambda option: f"{option} - {options[option]}",
        )

        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button(
                "Responder",
                key=f"battle_answer_{question['id']}_{battle['question_wrong_attempts']}",
                disabled=selected is None,
                use_container_width=True,
            ):
                answer_question(question, selected)
        with action_cols[1]:
            if st.button(
                "Pedir dica",
                key=f"battle_hint_{question['id']}_{battle['question_wrong_attempts']}",
                use_container_width=True,
            ):
                request_hint(question, selected)


def render_errors() -> None:
    tactical_logo()
    render_top_nav()
    st.markdown("### Caderno de Erros")
    errors = db.list_active_errors()
    if not errors:
        st.info("Nenhum erro ativo. O caderno está limpo.")
        return

    for error in errors:
        with st.expander(f"{error['enemy_name']} - {error['skill_tag']}"):
            st.markdown(f"**Tema:** {error['topic']}")
            st.markdown(f"**Tipo de erro:** {error['error_type']}")
            st.markdown(f"**Fraqueza:** {error['weakness']}")
            st.markdown(f"**Proxima revisao:** {error['review_due_at']}")
            st.markdown(f"**Questao:** {error['stem']}")
            st.markdown(f"**Resposta marcada:** {error['selected_option']}")
            st.markdown(f"**Dica recebida:** {error['hint_received']}")
            if st.button("Revisar agora", key=f"review_{error['id']}"):
                db.resolve_error(error["id"])
                st.rerun()


def render_evolution() -> None:
    player = current_player()
    progress = db.get_phase_progress()
    stats = db.evolution_stats()

    tactical_logo()
    render_top_nav()
    st.markdown("### Painel de Evolucao")

    cols = st.columns(4)
    with cols[0]:
        stat_card("XP total", player["xp"], f"Nivel {player['level']}")
    with cols[1]:
        stat_card("ELO", player["chemistry_elo"], "Quimica Quantitativa")
    with cols[2]:
        stat_card("Fase atual", PHASES[player["current_phase"]]["name"], PHASES[player["current_phase"]]["topic"])
    with cols[3]:
        boss_defeated = "Sim" if progress["fase_3"]["completed"] else "Nao"
        stat_card("Molock derrotado", boss_defeated, "Boss final")

    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.markdown("#### Acertos por skill_tag")
        correct_by_skill = stats["correct_by_skill"]
        if correct_by_skill:
            frame = pd.DataFrame(
                [{"skill_tag": key, "acertos": value} for key, value in correct_by_skill.items()]
            ).set_index("skill_tag")
            st.bar_chart(frame)
        else:
            st.caption("Sem acertos registrados ainda.")

    with chart_cols[1]:
        st.markdown("#### Erros ativos por tipo")
        wrong_by_type = stats["wrong_by_type"]
        if wrong_by_type:
            frame = pd.DataFrame(
                [{"tipo": key, "erros": value} for key, value in wrong_by_type.items()]
            ).set_index("tipo")
            st.bar_chart(frame)
        else:
            st.caption("Sem erros ativos.")

    st.markdown("#### Tentativas recentes")
    attempts = stats["attempts"][:12]
    if attempts:
        table = pd.DataFrame(attempts)[
            ["question_id", "selected_option", "is_correct", "attempt_number", "hint_level", "xp_gain", "elo_before", "elo_after", "created_at"]
        ]
        st.dataframe(table, use_container_width=True, hide_index=True)
    else:
        st.caption("Nenhuma tentativa registrada.")


def main() -> None:
    bootstrap()
    view = st.session_state["view"]
    if view == "campaign":
        render_campaign()
    elif view == "battle":
        render_battle()
    elif view == "errors":
        render_errors()
    elif view == "evolution":
        render_evolution()
    else:
        render_home()


if __name__ == "__main__":
    main()
