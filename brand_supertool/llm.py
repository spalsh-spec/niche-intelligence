"""Thin Anthropic wrapper with graceful no-key fallback.

The whole tool works WITHOUT this — every consumer must handle a None return
and fall back to deterministic heuristics. When ANTHROPIC_API_KEY is set the
same calls return richer, model-written output.
"""
from __future__ import annotations

import json
from typing import List, Optional

from . import config

_client = None
_tried = False


def _get_client():
    global _client, _tried
    if _tried:
        return _client
    _tried = True
    if not config.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic  # type: ignore
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    except Exception as exc:  # pragma: no cover
        print(f"[llm] anthropic unavailable ({exc}); heuristic mode")
        _client = None
    return _client


def available() -> bool:
    return _get_client() is not None


def complete(prompt: str, system: Optional[str] = None,
             max_tokens: int = 1024) -> Optional[str]:
    client = _get_client()
    if client is None:
        return None
    try:
        kwargs = dict(model=config.ANTHROPIC_MODEL, max_tokens=max_tokens,
                      messages=[{"role": "user", "content": prompt}])
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    except Exception as exc:  # pragma: no cover
        print(f"[llm] completion failed ({exc})")
        return None


def complete_json(prompt: str, system: Optional[str] = None,
                  max_tokens: int = 1024):
    """Ask for JSON; return parsed object or None."""
    text = complete(prompt + "\n\nReturn ONLY valid JSON.", system, max_tokens)
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1].lstrip("json").strip()
    try:
        return json.loads(text)
    except Exception:
        return None
