from __future__ import annotations

import html
from typing import Any

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ap-bg: oklch(0.135 0.025 235);
            --ap-deck: oklch(0.18 0.027 230);
            --ap-panel: oklch(0.215 0.033 232);
            --ap-panel-2: oklch(0.255 0.035 232);
            --ap-border: oklch(0.43 0.045 222);
            --ap-border-hot: oklch(0.64 0.16 31);
            --ap-text: oklch(0.91 0.026 220);
            --ap-muted: oklch(0.68 0.045 220);
            --ap-cyan: oklch(0.78 0.16 205);
            --ap-green: oklch(0.78 0.17 153);
            --ap-red: oklch(0.68 0.19 27);
            --ap-amber: oklch(0.82 0.16 78);
            --ap-violet: oklch(0.62 0.13 292);
            --ap-shadow: oklch(0.07 0.018 235 / 0.62);
            --space-xs: 0.35rem;
            --space-sm: 0.65rem;
            --space-md: 1rem;
            --space-lg: 1.45rem;
            --space-xl: 2.1rem;
        }
        .stApp {
            background:
                radial-gradient(circle at 16% 8%, oklch(0.62 0.13 205 / 0.16), transparent 28%),
                radial-gradient(circle at 84% 18%, oklch(0.68 0.16 31 / 0.12), transparent 24%),
                linear-gradient(135deg, oklch(0.12 0.025 238) 0%, oklch(0.155 0.024 228) 56%, oklch(0.16 0.03 248) 100%);
            color: var(--ap-text);
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(oklch(0.72 0.08 210 / 0.055) 1px, transparent 1px),
                linear-gradient(90deg, oklch(0.72 0.08 210 / 0.045) 1px, transparent 1px);
            background-size: 42px 42px;
            mask-image: linear-gradient(to bottom, black, transparent 74%);
        }
        .block-container { padding-top: 1rem; max-width: 1240px; }
        h1, h2, h3 { letter-spacing: 0 !important; }
        h3 { margin-bottom: 0.55rem; }
        div[data-testid="stHeader"] { background: transparent; }
        div[data-testid="stMetricValue"] { color: var(--ap-text); }
        div.stButton > button {
            min-height: 42px;
            border: 1px solid oklch(0.55 0.08 214 / 0.72);
            border-radius: 5px;
            background:
                linear-gradient(180deg, oklch(0.29 0.055 224 / 0.94), oklch(0.2 0.04 228 / 0.94));
            color: var(--ap-text);
            font-weight: 760;
            text-transform: uppercase;
            letter-spacing: 0.045em;
            box-shadow: 0 10px 22px var(--ap-shadow), inset 0 1px 0 oklch(0.82 0.08 210 / 0.13);
            transition: transform 160ms cubic-bezier(.25,1,.5,1), border-color 160ms cubic-bezier(.25,1,.5,1), background 160ms cubic-bezier(.25,1,.5,1);
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            border-color: var(--ap-cyan);
            background: linear-gradient(180deg, oklch(0.34 0.07 218), oklch(0.23 0.045 226));
        }
        div.stButton > button:active { transform: translateY(1px); }
        div.stButton > button:disabled {
            opacity: 0.45;
            filter: grayscale(0.5);
        }
        div[role="radiogroup"] label {
            border: 1px solid oklch(0.39 0.045 224);
            background: oklch(0.18 0.026 232 / 0.88);
            border-radius: 6px;
            padding: 0.7rem 0.8rem;
            margin-bottom: 0.45rem;
        }
        div[role="radiogroup"] label:hover {
            border-color: oklch(0.64 0.12 205);
            background: oklch(0.24 0.04 228 / 0.92);
        }
        .command-shell {
            position: relative;
            border: 1px solid oklch(0.5 0.07 215);
            border-radius: 8px;
            background:
                linear-gradient(90deg, oklch(0.28 0.055 222 / 0.78), oklch(0.18 0.027 234 / 0.92)),
                repeating-linear-gradient(135deg, oklch(0.78 0.12 205 / 0.08) 0 1px, transparent 1px 16px);
            box-shadow: 0 22px 60px var(--ap-shadow), inset 0 1px 0 oklch(0.9 0.04 210 / 0.08);
            padding: var(--space-lg);
            margin-bottom: var(--space-md);
            overflow: hidden;
        }
        .command-shell::after {
            content: "";
            position: absolute;
            inset: auto 0 0 0;
            height: 3px;
            background: linear-gradient(90deg, var(--ap-cyan), transparent 36%, var(--ap-amber), transparent 78%);
            opacity: 0.86;
        }
        .command-topline {
            display: flex;
            justify-content: space-between;
            gap: var(--space-md);
            align-items: flex-start;
        }
        .command-brand h1 {
            margin: 0;
            color: var(--ap-text);
            font-size: 2.35rem;
            line-height: 1;
            font-weight: 900;
        }
        .command-brand p {
            margin: 0.45rem 0 0;
            color: var(--ap-muted);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.12em;
        }
        .command-meta {
            display: grid;
            gap: 0.4rem;
            justify-items: end;
            min-width: 220px;
        }
        .system-chip, .phase-tag {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            padding: 0.28rem 0.55rem;
            border: 1px solid oklch(0.56 0.095 205 / 0.8);
            border-radius: 4px;
            background: oklch(0.21 0.035 228 / 0.72);
            color: var(--ap-cyan);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .system-chip.hot {
            border-color: oklch(0.68 0.15 31 / 0.82);
            color: var(--ap-amber);
        }
        .pilot-hud {
            display: grid;
            grid-template-columns: 1.25fr repeat(4, minmax(120px, 1fr));
            gap: var(--space-sm);
            margin: var(--space-md) 0 var(--space-lg);
        }
        .hud-cell {
            border: 1px solid oklch(0.38 0.05 222);
            background:
                linear-gradient(180deg, oklch(0.23 0.034 231 / 0.93), oklch(0.17 0.026 235 / 0.94));
            border-radius: 6px;
            padding: 0.85rem;
            min-height: 86px;
            box-shadow: inset 0 1px 0 oklch(0.9 0.03 210 / 0.055);
        }
        .hud-cell.primary {
            background:
                linear-gradient(135deg, oklch(0.3 0.06 225 / 0.94), oklch(0.2 0.028 238 / 0.95));
        }
        .hud-value {
            color: var(--ap-text);
            font-size: 1.55rem;
            line-height: 1.1;
            font-weight: 850;
            margin-top: 0.25rem;
        }
        .hud-detail {
            color: var(--ap-muted);
            font-size: 0.82rem;
            margin-top: 0.35rem;
        }
        .mission-briefing {
            display: grid;
            grid-template-columns: minmax(0, 1.4fr) minmax(270px, 0.8fr);
            gap: var(--space-md);
            align-items: stretch;
            margin-bottom: var(--space-lg);
        }
        .brief-main, .threat-card, .combat-question, .enemy-dossier, .mentor-comms, .boss-comms, .ap-card {
            border: 1px solid var(--ap-border);
            border-radius: 8px;
            background: linear-gradient(180deg, oklch(0.22 0.03 232 / 0.94), oklch(0.16 0.024 236 / 0.94));
            box-shadow: 0 16px 38px var(--ap-shadow), inset 0 1px 0 oklch(0.9 0.04 210 / 0.055);
        }
        .brief-main {
            padding: var(--space-lg);
        }
        .brief-main h2 {
            margin: 0.6rem 0 0.7rem;
            font-size: 1.55rem;
            line-height: 1.15;
        }
        .threat-card {
            padding: var(--space-md);
        }
        .threat-name {
            font-size: 1.2rem;
            font-weight: 850;
            margin-top: 0.5rem;
            color: var(--ap-amber);
        }
        .progress-rail {
            display: flex;
            gap: 0.45rem;
            margin-top: var(--space-md);
        }
        .progress-cell {
            height: 10px;
            flex: 1;
            border: 1px solid oklch(0.38 0.045 222);
            background: oklch(0.16 0.022 235);
            border-radius: 2px;
        }
        .progress-cell.done { background: var(--ap-green); }
        .progress-cell.current { background: var(--ap-cyan); }
        .ap-logo {
            border: 1px solid oklch(0.54 0.08 205 / 0.6);
            background: linear-gradient(90deg, oklch(0.24 0.045 224 / 0.86), oklch(0.17 0.026 235 / 0.84));
            padding: 18px 20px;
            margin-bottom: 14px;
        }
        .ap-logo h1 {
            margin: 0;
            color: var(--ap-text);
            font-size: 2rem;
            font-weight: 800;
        }
        .ap-logo p {
            color: var(--ap-muted);
            margin: 4px 0 0;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
        }
        .ap-card { padding: 16px; min-height: 112px; }
        .ap-card.locked {
            filter: grayscale(0.8);
            opacity: 0.58;
        }
        .ap-label {
            color: var(--ap-muted);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        .ap-value {
            color: var(--ap-text);
            font-size: 1.45rem;
            font-weight: 760;
            margin-top: 5px;
        }
        .hp-shell {
            width: 100%;
            height: 22px;
            border: 1px solid var(--ap-border);
            background:
                repeating-linear-gradient(90deg, oklch(0.36 0.04 225 / 0.22) 0 1px, transparent 1px 18px),
                oklch(0.11 0.02 238);
            border-radius: 3px;
            overflow: hidden;
            box-shadow: inset 0 0 12px oklch(0.06 0.02 238 / 0.7);
        }
        .hp-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--ap-red), var(--ap-amber));
            box-shadow: 0 0 18px oklch(0.7 0.16 31 / 0.3);
        }
        .hp-fill.player {
            background: linear-gradient(90deg, var(--ap-green), var(--ap-cyan));
            box-shadow: 0 0 18px oklch(0.74 0.14 205 / 0.28);
        }
        .battle-grid {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 14px;
            margin-top: 12px;
        }
        .mentor, .boss-line { display: none; }
        .phase-tag { margin-bottom: 8px; }
        .small-muted { color: var(--ap-muted); font-size: 0.86rem; }
        .history-line {
            border-bottom: 1px solid rgba(45,58,73,0.62);
            padding: 8px 0;
            color: oklch(0.81 0.035 220);
        }
        .ap-svg {
            width: 100%;
            max-height: 240px;
            border: 1px solid var(--ap-border);
            border-radius: 8px;
            background: oklch(0.15 0.027 235);
        }
        div[data-testid="stImage"] img {
            border: 1px solid var(--ap-border);
            border-radius: 8px;
            background: oklch(0.15 0.027 235);
            box-shadow: 0 18px 44px var(--ap-shadow), inset 0 1px 0 oklch(0.92 0.04 210 / 0.06);
        }
        .campaign-map {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: var(--space-md);
            align-items: stretch;
            margin-top: var(--space-md);
        }
        .mission-node {
            position: relative;
            min-height: 230px;
            padding: var(--space-md);
            border: 1px solid var(--ap-border);
            border-radius: 8px;
            background:
                radial-gradient(circle at 86% 10%, oklch(0.78 0.16 205 / 0.12), transparent 24%),
                linear-gradient(180deg, oklch(0.23 0.035 230 / 0.95), oklch(0.155 0.023 236 / 0.96));
            box-shadow: 0 18px 42px var(--ap-shadow);
            overflow: hidden;
        }
        .mission-node.locked {
            opacity: 0.48;
            filter: grayscale(0.82);
        }
        .node-number {
            display: grid;
            place-items: center;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: 1px solid oklch(0.6 0.12 205);
            color: var(--ap-cyan);
            font-weight: 900;
            font-size: 1rem;
            background: oklch(0.16 0.028 235);
            margin-bottom: var(--space-md);
        }
        .mission-node h3 {
            margin: 0.2rem 0 0.65rem;
            font-size: 1.1rem;
            line-height: 1.18;
        }
        .node-footer {
            margin-top: var(--space-md);
            display: flex;
            justify-content: space-between;
            gap: var(--space-sm);
            color: var(--ap-muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
        }
        .battle-arena {
            border: 1px solid oklch(0.52 0.075 215);
            border-radius: 8px;
            padding: var(--space-md);
            background:
                radial-gradient(circle at 82% 4%, oklch(0.67 0.18 31 / 0.12), transparent 30%),
                linear-gradient(180deg, oklch(0.19 0.03 232 / 0.96), oklch(0.13 0.024 238 / 0.97));
            box-shadow: 0 20px 60px var(--ap-shadow), inset 0 1px 0 oklch(0.92 0.04 210 / 0.06);
            margin-top: var(--space-md);
        }
        .arena-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: var(--space-md);
            margin-bottom: var(--space-md);
        }
        .arena-title h2 {
            margin: 0;
            font-size: 1.45rem;
        }
        .combat-question {
            padding: var(--space-lg);
            margin-bottom: var(--space-md);
        }
        .combat-question h3 {
            font-size: 1.24rem;
            line-height: 1.38;
            margin: 0.7rem 0 0;
            max-width: 72ch;
        }
        .enemy-dossier {
            padding: var(--space-md);
            margin-bottom: var(--space-md);
        }
        .enemy-dossier h3 {
            color: var(--ap-amber);
            margin: 0.55rem 0 0.35rem;
        }
        .mentor-comms, .boss-comms {
            padding: var(--space-md);
            margin-top: var(--space-sm);
        }
        .mentor-comms {
            border-color: oklch(0.57 0.1 205);
            background: linear-gradient(180deg, oklch(0.23 0.045 215 / 0.95), oklch(0.16 0.027 236 / 0.96));
            color: oklch(0.9 0.05 205);
        }
        .boss-comms {
            border-color: oklch(0.6 0.14 31);
            background: linear-gradient(180deg, oklch(0.24 0.05 30 / 0.9), oklch(0.16 0.026 238 / 0.96));
            color: oklch(0.93 0.05 50);
        }
        .comms-label {
            color: var(--ap-muted);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            margin-bottom: 0.45rem;
        }
        .battle-history {
            border: 1px solid oklch(0.34 0.04 224);
            background: oklch(0.15 0.022 236 / 0.72);
            border-radius: 8px;
            padding: var(--space-sm) var(--space-md);
        }
        @media (max-width: 900px) {
            .command-topline, .mission-briefing, .pilot-hud, .campaign-map {
                grid-template-columns: 1fr;
                display: grid;
            }
            .command-meta { justify-items: start; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def tactical_logo() -> None:
    st.markdown(
        """
        <div class="command-shell">
          <div class="command-topline">
            <div class="command-brand">
              <h1>PROTOCOLO APOGEU</h1>
              <p>Comando local de Quimica Quantitativa</p>
            </div>
            <div class="command-meta">
              <span class="system-chip">Offline first</span>
              <span class="system-chip hot">Ameaça: Molock</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pilot_hud(player: dict[str, Any], completed_phases: int, current_phase_name: str) -> None:
    st.markdown(
        f"""
        <div class="pilot-hud">
          <div class="hud-cell primary">
            <div class="ap-label">Cadete</div>
            <div class="hud-value">{html.escape(str(player["name"]))}</div>
            <div class="hud-detail">{html.escape(current_phase_name)}</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">Nivel</div>
            <div class="hud-value">{player["level"]}</div>
            <div class="hud-detail">{player["xp"]} XP total</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">ELO Quimica</div>
            <div class="hud-value">{player["chemistry_elo"]}</div>
            <div class="hud-detail">rating de combate</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">HP</div>
            <div class="hud-value">{player["hp"]}</div>
            <div class="hud-detail">pronto para batalha</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">Campanha</div>
            <div class="hud-value">{completed_phases}/3</div>
            <div class="hud-detail">setores vencidos</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mission_briefing(current_phase: dict[str, Any], completed_phases: int) -> None:
    cells = []
    for index in range(3):
        css_class = "done" if index < completed_phases else ("current" if index == completed_phases else "")
        cells.append(f'<div class="progress-cell {css_class}"></div>')
    st.markdown(
        f"""
        <div class="mission-briefing">
          <div class="brief-main">
            <span class="phase-tag">{html.escape(current_phase["title"])}</span>
            <h2>{html.escape(current_phase["objective"])}</h2>
            <div class="small-muted">Tema: {html.escape(current_phase["topic"])}</div>
            <div class="progress-rail">{''.join(cells)}</div>
          </div>
          <div class="threat-card">
            <div class="ap-label">Dossiê hostil</div>
            <div class="threat-name">{html.escape(current_phase["enemy_name"])}</div>
            <div class="hud-detail">Pressa, confusão de unidade e erro de proporção.</div>
            <div class="node-footer"><span>HP base</span><span>{current_phase["enemy_hp"]}</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: Any, detail: str = "") -> None:
    st.markdown(
        f"""
        <div class="ap-card">
          <div class="ap-label">{html.escape(str(label))}</div>
          <div class="ap-value">{html.escape(str(value))}</div>
          <div class="small-muted">{html.escape(str(detail))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hp_bar(label: str, current: int, total: int, player: bool = False) -> None:
    pct = 0 if total <= 0 else max(0, min(100, round(current / total * 100)))
    css_class = "player" if player else ""
    st.markdown(
        f"""
        <div class="ap-label">{html.escape(label)}: {current}/{total}</div>
        <div class="hp-shell"><div class="hp-fill {css_class}" style="width:{pct}%"></div></div>
        """,
        unsafe_allow_html=True,
    )


def phase_card(phase: dict[str, Any]) -> None:
    locked_class = "" if phase["unlocked"] else " locked"
    status = "Concluida" if phase["completed"] else ("Liberada" if phase["unlocked"] else "Bloqueada")
    number = {"fase_1": "01", "fase_2": "02", "fase_3": "B"}.get(phase["id"], "??")
    st.markdown(
        f"""
        <div class="mission-node{locked_class}">
          <div class="node-number">{number}</div>
          <span class="phase-tag">{html.escape(status)}</span>
          <h3>{html.escape(phase["title"])}</h3>
          <p class="small-muted">{html.escape(phase["topic"])}</p>
          <p>{html.escape(phase["objective"])}</p>
          <div class="node-footer"><span>HP inimigo {phase["enemy_hp"]}</span><span>Score {phase["best_score"]}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def boss_svg() -> None:
    st.image("assets/molock-boss.png", width="stretch")


def battle_arena_header(phase: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="battle-arena">
          <div class="arena-title">
            <div>
              <span class="phase-tag">Arena ativa</span>
              <h2>{html.escape(phase["title"])}</h2>
            </div>
            <span class="system-chip hot">{html.escape(phase["enemy_name"])}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def combat_question(question: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="combat-question">
          <span class="phase-tag">{html.escape(question["topic"])} | dificuldade {question["difficulty"]}</span>
          <h3>{html.escape(question["stem"])}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def enemy_dossier(phase: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="enemy-dossier">
          <div class="ap-label">Boss em campo</div>
          <h3>{html.escape(phase["enemy_name"])}</h3>
          <div class="small-muted">{html.escape(phase["topic"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mentor_panel(text: str) -> None:
    st.markdown(
        f"""
        <div class="mentor-comms">
          <div class="comms-label">Comms Mentor: Vetor</div>
          <div>{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def boss_line(text: str) -> None:
    st.markdown(
        f"""
        <div class="boss-comms">
          <div class="comms-label">Canal hostil</div>
          <div>{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
