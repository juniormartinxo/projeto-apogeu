from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

from src.game_logic import fallback_boss_taunt
from src.prompts import BOSS_SYSTEM_PROMPT, MENTOR_SYSTEM_PROMPT


OLLAMA_CHAT_URL = os.environ.get("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL = "gpt-oss:20b"


def ollama_model() -> str:
    return os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)


def _chat(system_prompt: str, payload: dict[str, Any], timeout: float = 4.0) -> str:
    response = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": ollama_model(),
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "options": {"temperature": 0.4, "num_predict": 80},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return str(data.get("message", {}).get("content", "")).strip()


def _compact(text: str, max_chars: int = 220) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "..."


def _mentor_fallback(context: dict[str, Any]) -> str:
    allowed_hint = context.get("allowed_hint") or "Volte um passo. Identifique unidade, mol e proporcao antes de calcular."
    if context.get("hint_level") == 1 and context.get("error_type") != "nao identificado":
        allowed_hint = f"Erro de {context['error_type']}."
    return f"Vetor: {_compact(str(allowed_hint), 180)}"


def _safe_mentor_text(text: str, context: dict[str, Any]) -> str:
    blocked_patterns = [
        r"alternativa correta",
        r"op[cç][aã]o correta",
        r"resposta final",
        r"o resultado [eé]",
        r"gabarito",
    ]
    lowered = text.lower()
    if any(re.search(pattern, lowered) for pattern in blocked_patterns):
        return _mentor_fallback(context)
    return f"Vetor: {_compact(text, 180)}"


def get_mentor_hint(context: dict[str, Any]) -> str:
    if os.environ.get("APOGEU_DISABLE_OLLAMA") == "1":
        return _mentor_fallback(context)

    try:
        text = _chat(MENTOR_SYSTEM_PROMPT, context)
    except Exception:
        return _mentor_fallback(context)

    if not text:
        return _mentor_fallback(context)
    return _safe_mentor_text(text, context)


def get_boss_taunt(context: dict[str, Any]) -> str:
    if os.environ.get("APOGEU_DISABLE_OLLAMA") == "1":
        return fallback_boss_taunt(context)

    try:
        text = _chat(BOSS_SYSTEM_PROMPT, context, timeout=3.0)
    except Exception:
        return fallback_boss_taunt(context)

    if not text:
        return fallback_boss_taunt(context)
    lowered = text.lower()
    blocked = ["use ", "calcule", "dica", "coeficiente conversa", "massa para mol"]
    if any(term in lowered for term in blocked):
        return fallback_boss_taunt(context)
    return f"Molock: {_compact(text, 160).removeprefix('Molock:').strip()}"
