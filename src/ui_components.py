from __future__ import annotations

import html
from typing import Any

import streamlit as st


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _pct(current: int, total: int) -> int:
    if total <= 0:
        return 0
    return max(0, min(100, round(current / total * 100)))


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ap-bg: oklch(0.125 0.028 236);
            --ap-deck: oklch(0.165 0.032 232);
            --ap-panel: oklch(0.215 0.038 230);
            --ap-panel-2: oklch(0.27 0.046 224);
            --ap-line: oklch(0.52 0.075 210);
            --ap-line-soft: oklch(0.38 0.052 218);
            --ap-text: oklch(0.92 0.028 214);
            --ap-muted: oklch(0.69 0.045 218);
            --ap-cyan: oklch(0.79 0.16 202);
            --ap-green: oklch(0.77 0.17 154);
            --ap-red: oklch(0.66 0.2 28);
            --ap-amber: oklch(0.82 0.17 76);
            --ap-violet: oklch(0.66 0.15 284);
            --ap-shadow: oklch(0.06 0.018 236 / 0.68);
            --space-xs: 0.35rem;
            --space-sm: 0.65rem;
            --space-md: 1rem;
            --space-lg: 1.45rem;
            --space-xl: 2.1rem;
        }
        .stApp {
            background:
                radial-gradient(circle at 14% 9%, oklch(0.72 0.15 202 / 0.16), transparent 25%),
                radial-gradient(circle at 86% 16%, oklch(0.75 0.17 31 / 0.14), transparent 28%),
                linear-gradient(135deg, oklch(0.11 0.025 238) 0%, oklch(0.145 0.027 226) 54%, oklch(0.13 0.036 250) 100%);
            color: var(--ap-text);
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(oklch(0.72 0.08 210 / 0.06) 1px, transparent 1px),
                linear-gradient(90deg, oklch(0.72 0.08 210 / 0.045) 1px, transparent 1px);
            background-size: 38px 38px;
            mask-image: linear-gradient(to bottom, black, transparent 76%);
        }
        .block-container {
            max-width: 1280px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stHeader"] { background: transparent; }
        h1, h2, h3 { letter-spacing: 0 !important; }
        h3 { margin-bottom: 0.55rem; }
        div.stButton > button {
            min-height: 44px;
            border: 1px solid oklch(0.56 0.09 210 / 0.78);
            border-radius: 5px;
            background:
                linear-gradient(180deg, oklch(0.31 0.06 220 / 0.96), oklch(0.2 0.04 230 / 0.98));
            color: var(--ap-text);
            font-weight: 840;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 12px 28px var(--ap-shadow), inset 0 1px 0 oklch(0.88 0.05 205 / 0.12);
            transition: transform 150ms cubic-bezier(.25,1,.5,1), border-color 150ms cubic-bezier(.25,1,.5,1), filter 150ms cubic-bezier(.25,1,.5,1);
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            border-color: var(--ap-cyan);
            filter: brightness(1.08);
        }
        div.stButton > button:active { transform: translateY(1px); }
        div.stButton > button:disabled {
            opacity: 0.42;
            filter: grayscale(0.5);
        }
        .command-shell {
            position: relative;
            border: 1px solid oklch(0.58 0.09 205 / 0.75);
            border-radius: 8px;
            background:
                linear-gradient(90deg, oklch(0.29 0.06 222 / 0.82), oklch(0.17 0.028 235 / 0.93)),
                repeating-linear-gradient(135deg, oklch(0.78 0.12 205 / 0.08) 0 1px, transparent 1px 16px);
            box-shadow: 0 24px 66px var(--ap-shadow), inset 0 1px 0 oklch(0.9 0.04 210 / 0.08);
            padding: var(--space-lg);
            margin-bottom: var(--space-md);
            overflow: hidden;
        }
        .command-shell::after {
            content: "";
            position: absolute;
            inset: auto 0 0 0;
            height: 3px;
            background: linear-gradient(90deg, var(--ap-cyan), transparent 34%, var(--ap-amber), transparent 78%);
            opacity: 0.9;
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
            font-size: clamp(2.2rem, 4vw, 4.2rem);
            line-height: 0.94;
            font-weight: 950;
        }
        .command-brand p {
            margin: 0.65rem 0 0;
            color: var(--ap-muted);
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0.12em;
        }
        .command-meta {
            display: grid;
            gap: 0.45rem;
            justify-items: end;
            min-width: 225px;
        }
        .system-chip, .phase-tag, .error-badge {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            padding: 0.3rem 0.58rem;
            border: 1px solid oklch(0.56 0.095 205 / 0.8);
            border-radius: 4px;
            background: oklch(0.2 0.035 228 / 0.76);
            color: var(--ap-cyan);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .system-chip.hot, .phase-tag.hot, .error-badge.hot {
            border-color: oklch(0.69 0.15 31 / 0.86);
            color: var(--ap-amber);
            background: oklch(0.24 0.048 32 / 0.72);
        }
        .pilot-hud, .battle-hud {
            display: grid;
            grid-template-columns: 1.35fr repeat(4, minmax(118px, 1fr));
            gap: var(--space-sm);
            margin: var(--space-md) 0 var(--space-lg);
        }
        .battle-hud {
            grid-template-columns: 1.25fr 1.25fr repeat(3, minmax(120px, 1fr));
        }
        .hud-cell, .telemetry-cell {
            border: 1px solid oklch(0.39 0.055 218);
            background:
                linear-gradient(180deg, oklch(0.23 0.036 230 / 0.94), oklch(0.16 0.026 236 / 0.96));
            border-radius: 6px;
            padding: 0.85rem;
            min-height: 86px;
            box-shadow: inset 0 1px 0 oklch(0.9 0.03 210 / 0.055);
        }
        .hud-cell.primary {
            background:
                radial-gradient(circle at 90% 12%, oklch(0.77 0.13 202 / 0.16), transparent 28%),
                linear-gradient(135deg, oklch(0.3 0.064 224 / 0.96), oklch(0.18 0.028 238 / 0.96));
        }
        .hud-value {
            color: var(--ap-text);
            font-size: 1.48rem;
            line-height: 1.1;
            font-weight: 880;
            margin-top: 0.25rem;
        }
        .hud-detail, .small-muted {
            color: var(--ap-muted);
            font-size: 0.84rem;
            margin-top: 0.35rem;
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
            font-weight: 800;
            margin-top: 5px;
        }
        .mission-briefing {
            display: grid;
            grid-template-columns: minmax(0, 1.45fr) minmax(270px, 0.8fr);
            gap: var(--space-md);
            align-items: stretch;
            margin-bottom: var(--space-lg);
        }
        .brief-main, .threat-card, .combat-question, .enemy-dossier, .mentor-comms, .boss-comms, .ap-card,
        .boss-panel, .mentor-hologram, .combat-result, .bestiary-card, .telemetry-panel, .tactical-explanation {
            border: 1px solid var(--ap-line-soft);
            border-radius: 8px;
            background: linear-gradient(180deg, oklch(0.22 0.032 232 / 0.94), oklch(0.155 0.024 236 / 0.96));
            box-shadow: 0 16px 40px var(--ap-shadow), inset 0 1px 0 oklch(0.9 0.04 210 / 0.055);
        }
        .brief-main { padding: var(--space-lg); }
        .brief-main h2 {
            margin: 0.6rem 0 0.7rem;
            font-size: 1.55rem;
            line-height: 1.15;
        }
        .threat-card, .ap-card { padding: var(--space-md); }
        .threat-name {
            font-size: 1.24rem;
            font-weight: 880;
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
        .hp-shell {
            width: 100%;
            height: 20px;
            border: 1px solid var(--ap-line-soft);
            background:
                repeating-linear-gradient(90deg, oklch(0.36 0.04 225 / 0.22) 0 1px, transparent 1px 18px),
                oklch(0.105 0.02 238);
            border-radius: 3px;
            overflow: hidden;
            box-shadow: inset 0 0 12px oklch(0.06 0.02 238 / 0.72);
            margin-top: 0.45rem;
        }
        .hp-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--ap-red), var(--ap-amber));
            box-shadow: 0 0 18px oklch(0.7 0.16 31 / 0.34);
        }
        .hp-fill.player {
            background: linear-gradient(90deg, var(--ap-green), var(--ap-cyan));
            box-shadow: 0 0 18px oklch(0.74 0.14 205 / 0.3);
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
            min-height: 248px;
            padding: var(--space-md);
            border: 1px solid var(--ap-line-soft);
            border-radius: 8px;
            background:
                radial-gradient(circle at 86% 10%, oklch(0.78 0.16 205 / 0.13), transparent 25%),
                linear-gradient(180deg, oklch(0.23 0.035 230 / 0.96), oklch(0.15 0.023 236 / 0.97));
            box-shadow: 0 18px 44px var(--ap-shadow);
            overflow: hidden;
        }
        .mission-node::after {
            content: "";
            position: absolute;
            inset: auto 16px 14px 16px;
            height: 2px;
            background: linear-gradient(90deg, var(--ap-cyan), transparent, var(--ap-amber));
            opacity: 0.72;
        }
        .mission-node.locked {
            opacity: 0.5;
            filter: grayscale(0.82);
        }
        .node-number {
            display: grid;
            place-items: center;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 1px solid oklch(0.6 0.12 205);
            color: var(--ap-cyan);
            font-weight: 950;
            font-size: 1rem;
            background: oklch(0.16 0.028 235);
            margin-bottom: var(--space-md);
        }
        .mission-node h3 {
            margin: 0.25rem 0 0.65rem;
            font-size: 1.1rem;
            line-height: 1.18;
        }
        .node-footer, .bestiary-meta {
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
            border: 1px solid oklch(0.54 0.085 212);
            border-radius: 8px;
            padding: var(--space-md);
            background:
                radial-gradient(circle at 82% 4%, oklch(0.67 0.18 31 / 0.14), transparent 30%),
                linear-gradient(180deg, oklch(0.19 0.032 232 / 0.97), oklch(0.12 0.024 238 / 0.98));
            box-shadow: 0 20px 62px var(--ap-shadow), inset 0 1px 0 oklch(0.92 0.04 210 / 0.06);
            margin-top: var(--space-md);
            margin-bottom: var(--space-md);
        }
        .arena-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: var(--space-md);
        }
        .arena-title h2 {
            margin: 0;
            font-size: 1.5rem;
        }
        .combat-question {
            padding: var(--space-lg);
            margin-bottom: var(--space-md);
        }
        .combat-question h3 {
            font-size: 1.25rem;
            line-height: 1.38;
            margin: 0.7rem 0 0;
            max-width: 72ch;
        }
        .action-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: var(--space-sm);
            margin: var(--space-md) 0;
        }
        .action-card {
            min-height: 130px;
            border: 1px solid oklch(0.43 0.065 216);
            border-radius: 8px;
            padding: var(--space-md);
            background:
                radial-gradient(circle at 88% 10%, oklch(0.72 0.16 202 / 0.12), transparent 32%),
                linear-gradient(180deg, oklch(0.235 0.036 228 / 0.96), oklch(0.155 0.025 236 / 0.97));
            box-shadow: 0 14px 34px var(--ap-shadow), inset 0 1px 0 oklch(0.9 0.04 210 / 0.06);
        }
        .action-card.selected {
            border-color: var(--ap-cyan);
            background:
                radial-gradient(circle at 88% 10%, oklch(0.78 0.16 202 / 0.22), transparent 34%),
                linear-gradient(180deg, oklch(0.28 0.052 220 / 0.98), oklch(0.17 0.03 236 / 0.98));
            box-shadow: 0 0 0 1px oklch(0.8 0.12 202 / 0.16), 0 18px 42px var(--ap-shadow);
        }
        .action-id {
            width: 34px;
            height: 34px;
            display: grid;
            place-items: center;
            border: 1px solid var(--ap-line);
            border-radius: 50%;
            color: var(--ap-cyan);
            font-weight: 950;
            margin-bottom: 0.75rem;
            background: oklch(0.13 0.027 236);
        }
        .action-text {
            color: var(--ap-text);
            font-weight: 730;
            line-height: 1.34;
        }
        .attack-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--space-sm);
            margin-top: var(--space-sm);
        }
        .boss-panel {
            padding: var(--space-md);
            border-color: oklch(0.6 0.14 31);
            background:
                radial-gradient(circle at 50% 20%, oklch(0.75 0.18 31 / 0.18), transparent 32%),
                linear-gradient(180deg, oklch(0.25 0.052 30 / 0.94), oklch(0.13 0.025 238 / 0.97));
            animation: bossPulse 2200ms cubic-bezier(.25,1,.5,1) infinite;
        }
        .boss-panel h3 {
            margin: 0.35rem 0 0.4rem;
            color: var(--ap-amber);
            font-size: 1.35rem;
        }
        .boss-panel img {
            border: 1px solid oklch(0.58 0.12 31 / 0.72);
            border-radius: 8px;
            background: oklch(0.13 0.026 236);
            box-shadow: 0 18px 44px var(--ap-shadow);
        }
        @keyframes bossPulse {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.08); }
        }
        .mentor-hologram {
            padding: var(--space-md);
            margin-top: var(--space-sm);
            border-color: oklch(0.6 0.12 202);
            background:
                repeating-linear-gradient(180deg, oklch(0.79 0.12 202 / 0.08) 0 1px, transparent 1px 9px),
                linear-gradient(180deg, oklch(0.22 0.045 214 / 0.95), oklch(0.145 0.026 236 / 0.97));
            color: oklch(0.9 0.052 202);
        }
        .mentor-hologram .signal {
            color: var(--ap-cyan);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.45rem;
        }
        .boss-comms, .mentor-comms {
            padding: var(--space-md);
            margin-top: var(--space-sm);
        }
        .boss-comms {
            border-color: oklch(0.6 0.14 31);
            background: linear-gradient(180deg, oklch(0.24 0.05 30 / 0.9), oklch(0.16 0.026 238 / 0.96));
            color: oklch(0.93 0.05 50);
        }
        .mentor-comms {
            border-color: oklch(0.57 0.1 205);
            background: linear-gradient(180deg, oklch(0.23 0.045 215 / 0.95), oklch(0.16 0.027 236 / 0.96));
            color: oklch(0.9 0.05 205);
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
            background: oklch(0.145 0.022 236 / 0.74);
            border-radius: 8px;
            padding: var(--space-sm) var(--space-md);
            margin-top: var(--space-sm);
        }
        .history-line {
            border-bottom: 1px solid oklch(0.36 0.04 224 / 0.62);
            padding: 8px 0;
            color: oklch(0.81 0.035 220);
        }
        .combat-result {
            padding: var(--space-md);
            margin-bottom: var(--space-md);
        }
        .combat-result.effective {
            border-color: oklch(0.72 0.16 154);
            background:
                radial-gradient(circle at 90% 10%, oklch(0.77 0.17 154 / 0.14), transparent 30%),
                linear-gradient(180deg, oklch(0.22 0.043 160 / 0.9), oklch(0.15 0.024 236 / 0.97));
        }
        .combat-result.counter {
            border-color: oklch(0.68 0.18 31);
            background:
                radial-gradient(circle at 90% 10%, oklch(0.72 0.18 31 / 0.18), transparent 30%),
                linear-gradient(180deg, oklch(0.24 0.052 31 / 0.9), oklch(0.15 0.024 236 / 0.97));
        }
        .result-title {
            font-size: 1.08rem;
            font-weight: 920;
            color: var(--ap-text);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.65rem;
        }
        .result-grid, .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: var(--space-sm);
        }
        .result-stat, .telemetry-cell {
            border: 1px solid oklch(0.36 0.046 220);
            border-radius: 6px;
            background: oklch(0.13 0.024 236 / 0.68);
            padding: 0.75rem;
        }
        .tactical-explanation {
            padding: var(--space-md);
            margin-bottom: var(--space-md);
            border-color: oklch(0.58 0.1 202);
        }
        .bestiary-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: var(--space-md);
            margin-top: var(--space-md);
        }
        .bestiary-card {
            padding: var(--space-md);
            min-height: 250px;
            border-color: oklch(0.58 0.13 31 / 0.82);
            background:
                radial-gradient(circle at 88% 8%, oklch(0.72 0.18 31 / 0.13), transparent 30%),
                linear-gradient(180deg, oklch(0.225 0.038 230 / 0.96), oklch(0.14 0.024 236 / 0.98));
        }
        .bestiary-card h3 {
            color: var(--ap-amber);
            margin: 0.65rem 0 0.55rem;
            font-size: 1.2rem;
            line-height: 1.16;
        }
        .weakness-box {
            border: 1px solid oklch(0.5 0.08 202 / 0.7);
            border-radius: 6px;
            padding: 0.75rem;
            background: oklch(0.14 0.026 236 / 0.7);
            margin-top: 0.75rem;
        }
        .telemetry-panel {
            padding: var(--space-md);
            margin-top: var(--space-md);
        }
        .telemetry-row {
            display: grid;
            grid-template-columns: minmax(150px, 0.7fr) 1fr minmax(44px, 0.2fr);
            gap: var(--space-sm);
            align-items: center;
            padding: 0.55rem 0;
            border-bottom: 1px solid oklch(0.34 0.04 224 / 0.6);
        }
        .telemetry-bar {
            height: 9px;
            border: 1px solid oklch(0.4 0.05 220);
            border-radius: 2px;
            background: oklch(0.12 0.022 236);
            overflow: hidden;
        }
        .telemetry-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--ap-cyan), var(--ap-green));
        }
        .telemetry-fill.hot {
            background: linear-gradient(90deg, var(--ap-red), var(--ap-amber));
        }
        .attempt-feed {
            display: grid;
            gap: 0.55rem;
            margin-top: var(--space-sm);
        }
        .attempt-line {
            display: grid;
            grid-template-columns: minmax(80px, 0.4fr) 1fr minmax(72px, 0.35fr);
            gap: var(--space-sm);
            border: 1px solid oklch(0.34 0.04 224);
            border-radius: 6px;
            padding: 0.75rem;
            background: oklch(0.13 0.024 236 / 0.62);
        }
        .empty-state {
            border: 1px dashed oklch(0.42 0.05 220);
            border-radius: 8px;
            padding: var(--space-lg);
            color: var(--ap-muted);
            background: oklch(0.14 0.024 236 / 0.52);
        }
        @media (max-width: 900px) {
            .command-topline, .mission-briefing, .pilot-hud, .battle-hud, .campaign-map,
            .action-grid, .bestiary-grid, .result-grid, .telemetry-grid, .attack-row {
                grid-template-columns: 1fr;
                display: grid;
            }
            .command-meta { justify-items: start; }
            .attempt-line, .telemetry-row {
                grid-template-columns: 1fr;
            }
        }
        @media (prefers-reduced-motion: reduce) {
            .boss-panel { animation: none; }
            div.stButton > button { transition: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_game_title() -> None:
    st.markdown(
        """
        <div class="command-shell">
          <div class="command-topline">
            <div class="command-brand">
              <h1>PROTOCOLO APOGEU</h1>
              <p>Simulador tático de preparação ITA</p>
            </div>
            <div class="command-meta">
              <span class="system-chip">Central de Comando</span>
              <span class="system-chip hot">Ameaça ativa: Molock</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tactical_logo() -> None:
    render_game_title()


def pilot_hud(player: dict[str, Any], completed_phases: int, current_phase_name: str) -> None:
    st.markdown(
        f"""
        <div class="pilot-hud">
          <div class="hud-cell primary">
            <div class="ap-label">Cadete</div>
            <div class="hud-value">{_escape(player["name"])}</div>
            <div class="hud-detail">{_escape(current_phase_name)}</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">Nível</div>
            <div class="hud-value">{_escape(player["level"])}</div>
            <div class="hud-detail">{_escape(player["xp"])} XP total</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">ELO Química</div>
            <div class="hud-value">{_escape(player["chemistry_elo"])}</div>
            <div class="hud-detail">rating de combate</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">HP</div>
            <div class="hud-value">{_escape(player["hp"])}</div>
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
            <span class="phase-tag hot">Missão atual</span>
            <h2>{_escape(current_phase["objective"])}</h2>
            <div class="small-muted">Setor: {_escape(current_phase["title"])} | Tema: {_escape(current_phase["topic"])}</div>
            <div class="progress-rail">{''.join(cells)}</div>
          </div>
          <div class="threat-card">
            <div class="ap-label">Ameaça ativa</div>
            <div class="threat-name">{_escape(current_phase["enemy_name"])}</div>
            <div class="hud-detail">Pressa, confusão de unidade e erro de proporção.</div>
            <div class="node-footer"><span>HP base</span><span>{_escape(current_phase["enemy_hp"])}</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_command_center(player: dict[str, Any], current_phase: dict[str, Any], completed_phases: int) -> None:
    pilot_hud(player, completed_phases, current_phase["name"])
    mission_briefing(current_phase, completed_phases)


def stat_card(label: str, value: Any, detail: str = "") -> None:
    st.markdown(
        f"""
        <div class="ap-card">
          <div class="ap-label">{_escape(label)}</div>
          <div class="ap-value">{_escape(value)}</div>
          <div class="small-muted">{_escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hp_bar(label: str, current: int, total: int, player: bool = False) -> None:
    css_class = "player" if player else ""
    st.markdown(
        f"""
        <div class="ap-label">{_escape(label)}: {current}/{total}</div>
        <div class="hp-shell"><div class="hp-fill {css_class}" style="width:{_pct(current, total)}%"></div></div>
        """,
        unsafe_allow_html=True,
    )


def render_campaign_node(phase: dict[str, Any]) -> None:
    locked_class = "" if phase["unlocked"] else " locked"
    if phase["completed"]:
        status = "CONQUISTADO"
    elif phase["unlocked"]:
        status = "EM COMBATE"
    else:
        status = "BLOQUEADO"
    number = {"fase_1": "01", "fase_2": "02", "fase_3": "B"}.get(phase["id"], "??")
    badge_class = "phase-tag hot" if phase["unlocked"] and not phase["completed"] else "phase-tag"
    st.markdown(
        f"""
        <div class="mission-node{locked_class}">
          <div class="node-number">{number}</div>
          <span class="{badge_class}">{_escape(status)}</span>
          <h3>{_escape(phase["title"])}</h3>
          <p class="small-muted">{_escape(phase["topic"])}</p>
          <p>{_escape(phase["objective"])}</p>
          <div class="node-footer"><span>HP inimigo {phase["enemy_hp"]}</span><span>Score {phase["best_score"]}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def phase_card(phase: dict[str, Any]) -> None:
    render_campaign_node(phase)


def boss_svg() -> None:
    st.image("assets/molock-boss.png", width="stretch")


def battle_arena_header(phase: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="battle-arena">
          <div class="arena-title">
            <div>
              <span class="phase-tag hot">Arena ativa</span>
              <h2>{_escape(phase["title"])}</h2>
            </div>
            <span class="system-chip hot">{_escape(phase["enemy_name"])}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_battle_hud(
    player: dict[str, Any],
    phase: dict[str, Any],
    player_hp: int,
    max_player_hp: int,
    enemy_hp: int,
    max_enemy_hp: int,
) -> None:
    st.markdown(
        f"""
        <div class="battle-hud">
          <div class="hud-cell primary">
            <div class="ap-label">Cadete</div>
            <div class="hud-value">{_escape(player["name"])}</div>
            <div class="hud-detail">Fase: {_escape(phase["title"])}</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">HP do cadete</div>
            <div class="hud-value">{player_hp}/{max_player_hp}</div>
            <div class="hp-shell"><div class="hp-fill player" style="width:{_pct(player_hp, max_player_hp)}%"></div></div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">HP do boss</div>
            <div class="hud-value">{enemy_hp}/{max_enemy_hp}</div>
            <div class="hp-shell"><div class="hp-fill" style="width:{_pct(enemy_hp, max_enemy_hp)}%"></div></div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">XP</div>
            <div class="hud-value">{_escape(player["xp"])}</div>
            <div class="hud-detail">nível {_escape(player["level"])}</div>
          </div>
          <div class="hud-cell">
            <div class="ap-label">ELO Química</div>
            <div class="hud-value">{_escape(player["chemistry_elo"])}</div>
            <div class="hud-detail">rating ativo</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def combat_question(question: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="combat-question">
          <span class="phase-tag">Carta da questão | dificuldade {_escape(question["difficulty"])}</span>
          <h3>{_escape(question["stem"])}</h3>
          <div class="small-muted">Tema: {_escape(question["topic"])} | Skill: {_escape(question["skill_tag"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_cards(options: dict[str, str], selected_option: str | None, key_prefix: str) -> str | None:
    st.markdown('<div class="ap-label">CARTAS DE AÇÃO</div>', unsafe_allow_html=True)
    option_items = list(options.items())
    rows = [option_items[index : index + 2] for index in range(0, len(option_items), 2)]
    for row_index, row in enumerate(rows):
        cols = st.columns(len(row))
        for col, (option, text) in zip(cols, row):
            selected_class = " selected" if option == selected_option else ""
            with col:
                st.markdown(
                    f"""
                    <div class="action-card{selected_class}">
                      <div class="action-id">{_escape(option)}</div>
                      <div class="action-text">{_escape(text)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"EQUIPAR CARTA {option}",
                    key=f"{key_prefix}_{row_index}_{option}",
                    use_container_width=True,
                ):
                    selected_option = option
    return selected_option


def enemy_dossier(phase: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="enemy-dossier">
          <div class="ap-label">Boss em campo</div>
          <h3>{_escape(phase["enemy_name"])}</h3>
          <div class="small-muted">{_escape(phase["topic"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def boss_line(text: str) -> None:
    st.markdown(
        f"""
        <div class="boss-comms">
          <div class="comms-label">Canal hostil</div>
          <div>{_escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_boss_panel(phase: dict[str, Any], boss_text: str) -> None:
    st.markdown(
        f"""
        <div class="boss-panel">
          <div class="ap-label">Boss em campo</div>
          <h3>{_escape(phase["enemy_name"])}</h3>
          <div class="small-muted">{_escape(phase["topic"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    boss_svg()
    boss_line(boss_text)


def mentor_panel(text: str) -> None:
    st.markdown(
        f"""
        <div class="mentor-comms">
          <div class="comms-label">Comms Mentor: Vetor</div>
          <div>{_escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mentor_hologram(text: str, hint_level: int) -> None:
    st.markdown(
        f"""
        <div class="mentor-hologram">
          <div class="signal">Holograma tático | Vetor | Ajuda nível {hint_level}</div>
          <div>{_escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_combat_result(result: dict[str, Any]) -> None:
    if result["is_correct"]:
        title = "ATAQUE EFETIVO"
        css_class = "effective"
        stats = [
            ("Dano causado", result["damage_done"]),
            ("XP ganho", result["xp_gain"]),
            ("ELO", f"{result['elo_before']} -> {result['elo_after']}"),
        ]
    else:
        title = "CONTRA-ATAQUE DE MOLOCK"
        css_class = "counter"
        stats = [
            ("Dano recebido", result["damage_taken"]),
            ("Tipo de erro", result.get("error_type") or "nao identificado"),
            ("ELO", f"{result['elo_before']} -> {result['elo_after']}"),
        ]
    stat_html = "".join(
        f"""
        <div class="result-stat">
          <div class="ap-label">{_escape(label)}</div>
          <div class="ap-value">{_escape(value)}</div>
        </div>
        """
        for label, value in stats
    )
    st.markdown(
        f"""
        <div class="combat-result {css_class}">
          <div class="result-title">{title}</div>
          <div class="result-grid">{stat_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tactical_explanation(explanation: str) -> None:
    st.markdown(
        f"""
        <div class="tactical-explanation">
          <div class="ap-label">Explicação tática liberada</div>
          <div class="hud-detail">{_escape(explanation)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bestiary_card(error: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="bestiary-card">
          <span class="error-badge hot">{_escape(error["error_type"])}</span>
          <h3>{_escape(str(error["enemy_name"]).upper())}</h3>
          <div class="small-muted">Classe: {_escape(error["skill_tag"])}</div>
          <div class="weakness-box">
            <div class="ap-label">PONTO FRACO</div>
            <div>{_escape(error["weakness"])}</div>
          </div>
          <div class="bestiary-meta">
            <span>REAPARECE EM</span>
            <span>{_escape(error["review_due_at"])}</span>
          </div>
          <div class="small-muted">Última carta marcada: {_escape(error["selected_option"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_rows(title: str, values: dict[str, int], hot: bool = False) -> None:
    if not values:
        st.markdown(
            f"""
            <div class="telemetry-panel">
              <div class="result-title">{_escape(title)}</div>
              <div class="empty-state">Sem sinais registrados.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    maximum = max(values.values()) or 1
    rows = []
    fill_class = "telemetry-fill hot" if hot else "telemetry-fill"
    for label, value in values.items():
        rows.append(
            f"""
            <div class="telemetry-row">
              <div>{_escape(label)}</div>
              <div class="telemetry-bar"><div class="{fill_class}" style="width:{_pct(value, maximum)}%"></div></div>
              <div>{value}</div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div class="telemetry-panel">
          <div class="result-title">{_escape(title)}</div>
          {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recent_attempts(attempts: list[dict[str, Any]]) -> None:
    if not attempts:
        st.markdown('<div class="empty-state">Nenhuma tentativa registrada.</div>', unsafe_allow_html=True)
        return

    rows = []
    for attempt in attempts:
        outcome = "ACERTO" if attempt["is_correct"] else "ERRO"
        rows.append(
            f"""
            <div class="attempt-line">
              <div><span class="phase-tag">{_escape(outcome)}</span></div>
              <div>
                <div>{_escape(attempt["question_id"])} | {_escape(attempt["topic"])}</div>
                <div class="small-muted">Carta {_escape(attempt["selected_option"])} | tentativa {_escape(attempt["attempt_number"])} | dica {attempt["hint_level"]}</div>
              </div>
              <div class="small-muted">XP {attempt["xp_gain"]}<br>ELO {attempt.get("elo_before")} -> {attempt.get("elo_after")}</div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div class="telemetry-panel">
          <div class="result-title">Histórico de combate</div>
          <div class="attempt-feed">{''.join(rows)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
