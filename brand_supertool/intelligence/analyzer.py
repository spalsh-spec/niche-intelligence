"""Content feature extraction — the 'what is in this content' layer.

Deterministic heuristics produce a binary feature_flags map for every video
(title structure, hook style, thumbnail composition). These flags are the raw
material the pattern miner correlates against fuzzy performance.

When ANTHROPIC_API_KEY is present, analyze_thumbnail_vision() can enrich the
thumbnail features via Claude vision; the heuristics remain the dependable
floor so the corpus is always fully featurized.
"""
from __future__ import annotations

import re
from typing import Dict, List

from ..models import Video

# Human-readable labels for every feature key (used in reports / pattern text).
FEATURE_LABELS: Dict[str, str] = {
    "title.identity_trigger": "identity-aspiration title (\"become the man who…\", \"like a Greek…\")",
    "title.number": "number in the title",
    "title.curiosity_gap": "curiosity gap (\"the truth about\", \"nobody tells you\")",
    "title.first_person_result": "first-person result (\"I quit…\", \"I ate… here's my body\")",
    "title.freedom_negation": "freedom / anti-tracking framing (\"no scale\", \"without\")",
    "title.fear_clickbait": "fear / shouty clickbait (\"STOP\", \"killing your…\")",
    "hook.polarizing": "polarizing opening line",
    "hook.fear": "fear-based opening line",
    "thumb.shirtless": "shirtless physique on thumbnail",
    "thumb.sunlit": "warm / sunlit thumbnail",
    "thumb.outdoor": "outdoor (coast / mountain / beach) setting",
    "thumb.face": "visible face on thumbnail",
    "thumb.text_overlay": "text overlay on thumbnail",
    "thumb.shock_emotion": "shock / intense facial emotion",
}

_IDENTITY = re.compile(
    r"\b(become|the man|man who|who you|like a|like you|greek god|"
    r"fisherman|train like|eat like|the man you)\b", re.I)
_CURIOSITY = re.compile(
    r"\b(truth about|nobody|no one|here'?s|secret|what happened|"
    r"will tell you|the .* that)\b", re.I)
_FIRST_PERSON = re.compile(r"\bI (got|quit|ate|tried|train|threw|tested)\b", re.I)
_FREEDOM_NEG = re.compile(
    r"\b(no app|no scale|without|stop counting|no tracking|never)\b", re.I)
_FEAR = re.compile(
    r"(\bSTOP\b|killing|sabotag|mistakes?|destroy|before .* breakfast|"
    r"\bweak\b)", re.I)
_FEAR_HOOK = re.compile(r"(destroy|sabotag|killing|weak|lied|too late)", re.I)
_POLARIZING = re.compile(
    r"(upside down|everything you (were|are) told|lied|nobody (talks|tells)|"
    r"the body you want|made me weak)", re.I)


def extract_title_flags(title: str) -> Dict[str, bool]:
    return {
        "title.identity_trigger": bool(_IDENTITY.search(title)),
        "title.number": bool(re.search(r"\d", title)),
        "title.curiosity_gap": bool(_CURIOSITY.search(title)),
        "title.first_person_result": bool(_FIRST_PERSON.search(title)),
        "title.freedom_negation": bool(_FREEDOM_NEG.search(title)),
        # ALL-CAPS word of len>=3, or fear lexicon
        "title.fear_clickbait": bool(_FEAR.search(title)
                                     or re.search(r"\b[A-Z]{3,}\b", title)),
    }


def extract_hook_flags(hook: str) -> Dict[str, bool]:
    return {
        "hook.polarizing": bool(_POLARIZING.search(hook)),
        "hook.fear": bool(_FEAR_HOOK.search(hook)),
    }


def extract_thumb_flags(features: Dict) -> Dict[str, bool]:
    setting = str(features.get("setting", "")).lower()
    emotion = str(features.get("emotion", "")).lower()
    return {
        "thumb.shirtless": bool(features.get("shirtless")),
        "thumb.sunlit": bool(features.get("sunlit")),
        "thumb.outdoor": setting.startswith("outdoor"),
        "thumb.face": int(features.get("faces", 0)) > 0,
        "thumb.text_overlay": bool(str(features.get("text_overlay", "")).strip()),
        "thumb.shock_emotion": emotion in {"shock", "intense"},
    }


def analyze(video: Video) -> Video:
    flags: Dict[str, bool] = {}
    flags.update(extract_title_flags(video.title))
    flags.update(extract_hook_flags(video.hook))
    flags.update(extract_thumb_flags(video.thumbnail_features))
    video.feature_flags = flags
    video.analysis = {
        "present_features": [k for k, v in flags.items() if v],
        "title_len_words": len(video.title.split()),
    }
    return video


def analyze_corpus(videos: List[Video]) -> List[Video]:
    return [analyze(v) for v in videos]
