"""
AI module — summary, classification, label suggestion, reply generation.
Supports OpenAI (default) and Ollama (local fallback).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from issuesheriff.config import get_config

logger = logging.getLogger(__name__)

_ISSUE_TYPES = ["bug", "feature", "question", "docs", "chore", "security"]

_LABEL_MAP = {
    "bug": ["bug", "crash", "error", "fail", "broken", "exception", "regression", "fix"],
    "feature": ["feature", "request", "add", "support", "implement", "enhancement", "improve"],
    "question": ["question", "help", "how", "why", "what", "understand", "clarify", "usage"],
    "docs": ["doc", "readme", "wiki", "typo", "documentation", "example", "tutorial"],
    "security": ["vuln", "cve", "security", "inject", "xss", "csrf", "exploit", "auth"],
    "performance": ["slow", "memory", "cpu", "leak", "performance", "optimize", "speed"],
}


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def analyze_issue(title: str, body: str) -> dict:
    """
    Returns:
        {
          "summary": str,
          "type": str,
          "labels": list[str],
          "confidence": float
        }
    """
    prompt = _build_analysis_prompt(title, body)
    raw = _call_ai(prompt, expect_json=True)

    result = _safe_parse_json(raw)
    result.setdefault("summary", "No summary available.")
    result.setdefault("type", _classify_heuristic(title, body))
    result.setdefault("labels", suggest_labels(title, body, as_list=True))
    result.setdefault("confidence", 0.8)

    return result


def suggest_labels(title: str, body: str, as_list: bool = False) -> dict | list:
    """
    Returns dict[label -> confidence] or list[label] if as_list=True.
    Uses heuristic matching — no AI call needed for labels.
    """
    text = f"{title} {body}".lower()
    scores: dict[str, float] = {}

    for label, keywords in _LABEL_MAP.items():
        hits = sum(kw in text for kw in keywords)
        if hits >= 2:
            scores[label] = min(0.5 + hits * 0.15, 1.0)
        elif hits == 1:
            scores[label] = 0.4

    # Only keep labels with meaningful confidence
    scores = {k: v for k, v in scores.items() if v >= 0.5}

    # Fallback
    if not scores:
        scores = {"needs-triage": 0.5}

    # Sort by confidence
    scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

    if as_list:
        return list(scores.keys())[:3]
    return scores


def generate_reply(title: str, body: str) -> str:
    """Generate a maintainer reply draft."""
    prompt = _build_reply_prompt(title, body)
    return _call_ai(prompt, expect_json=False).strip()


# ─────────────────────────────────────────────
#  Prompts
# ─────────────────────────────────────────────

def _build_analysis_prompt(title: str, body: str) -> str:
    return f"""You are a senior open-source maintainer helping triage GitHub issues.

Analyze the following GitHub issue and return a JSON object with these fields:
- "summary": 2-3 sentence summary of the issue (plain text, no markdown)
- "type": one of {_ISSUE_TYPES}
- "labels": array of 1-3 relevant labels from {list(_LABEL_MAP.keys())}
- "confidence": float 0.0-1.0 how confident you are in the classification

Issue title: {title}
Issue body:
{body[:3000]}

Return ONLY valid JSON. No markdown, no explanation."""


def _build_reply_prompt(title: str, body: str) -> str:
    return f"""You are a friendly and professional open-source maintainer.
Write a short reply to the following GitHub issue.

The reply should:
1. Thank the user briefly
2. Show you understood the issue in 1 sentence
3. State next steps (triage, fix, asking for more info, etc.)

Keep it under 100 words. Be human, not corporate.

Issue title: {title}
Issue body:
{body[:2000]}

Reply (plain text only, no markdown headers):"""


# ─────────────────────────────────────────────
#  AI Backend
# ─────────────────────────────────────────────

def _call_ai(prompt: str, expect_json: bool = False) -> str:
    config = get_config()

    if config.openai_api_key:
        return _call_openai(prompt, config, expect_json)
    elif config.ollama_model:
        return _call_ollama(prompt, config)
    else:
        logger.debug("No AI backend configured — using heuristics only.")
        return "{}" if expect_json else "Thank you for the report. We will look into this."


def _call_openai(prompt: str, config: Any, expect_json: bool) -> str:
    try:
        import openai
        client = openai.OpenAI(api_key=config.openai_api_key)
        kwargs: dict = {
            "model": config.openai_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
            "temperature": 0.2,
        }
        if expect_json:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "{}" if expect_json else "Thank you for opening this issue!"


def _call_ollama(prompt: str, config: Any) -> str:
    try:
        import httpx
        response = httpx.post(
            f"{config.ollama_base_url}/api/generate",
            json={"model": config.ollama_model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return "{}"


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _classify_heuristic(title: str, body: str) -> str:
    text = f"{title} {body}".lower()
    scores = {t: 0 for t in _ISSUE_TYPES}

    keyword_map = {
        "bug": ["bug", "crash", "error", "broken", "fail", "exception", "regression"],
        "feature": ["feature", "request", "add", "implement", "support", "enhancement"],
        "question": ["question", "how", "why", "help", "understand", "what is"],
        "docs": ["documentation", "readme", "doc", "typo", "example"],
        "security": ["vulnerability", "security", "cve", "exploit"],
    }

    for t, keywords in keyword_map.items():
        scores[t] = sum(kw in text for kw in keywords)

    return max(scores, key=scores.get) if max(scores.values()) > 0 else "question"


def _safe_parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        # Strip markdown fences if present
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {}
