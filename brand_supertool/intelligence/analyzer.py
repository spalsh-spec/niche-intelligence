"""Content feature extraction — niche-agnostic.

Deterministic heuristics produce a binary feature_flags map for every video.
The features are universal across creator niches (identity framing, first-person
proof, specific systems, curiosity, list, fear clickbait, thumbnail composition),
so the same engine works for fitness, finance, philosophy, gaming, etc.
"""
from __future__ import annotations

import re
from typing import Dict, List

from ..models import Video

FEATURE_LABELS: Dict[str, str] = {
    "title.identity": "identity / aspiration framing (\"become the person who…\", \"the … mindset\")",
    "title.first_person": "first-person proof (\"I tried… here's what happened\")",
    "title.specific_system": "a specific system / method (\"the … system that works\", \"step by step\")",
    "title.curiosity_gap": "curiosity gap (\"the truth about\", \"nobody tells you\")",
    "title.number_list": "number / listicle in the title",
    "title.fear_clickbait": "fear / shouty clickbait (\"STOP\", \"before it's too late\")",
    "hook.polarizing": "polarizing opening line",
    "hook.fear": "fear-based opening line",
    "thumb.face": "visible face on thumbnail",
    "thumb.clean": "clean, uncluttered composition",
    "thumb.text_overlay": "text overlay on thumbnail",
    "thumb.expressive": "shock / intense facial emotion",
}

_IDENTITY = re.compile(
    r"\b(become|the kind of|the person who|the .* who|how to be|"
    r"mindset|identity|the man you|turn yourself)\b", re.I)
_FIRST_PERSON = re.compile(
    r"\bI (tried|built|quit|made|spent|tested|turned|grew|learned|started|ran)\b"
    r"|here'?s what happened|my results|\bfor \d+ days\b|\bin \d+ days\b", re.I)
_SPECIFIC = re.compile(
    r"\b(system|framework|method|protocol|exact|step[ -]by[ -]step|blueprint|"
    r"playbook|formula)\b|that (actually )?works", re.I)
_CURIOSITY = re.compile(
    r"truth about|nobody (tells|knows)|no one tells|secret|the real reason|"
    r"won'?t believe|what .* won'?t tell", re.I)
_FEAR = re.compile(
    r"(\bSTOP\b|\bmistakes?\b|killing|destroy|ruin|before it'?s too late|"
    r"\bwarning\b|\bworst\b|getting .* wrong|\bnever\b)", re.I)
_FEAR_HOOK = re.compile(
    r"(destroy|ruin|killing|too late|warning|weak|sabotag)", re.I)
_POLARIZING = re.compile(
    r"(nobody talks about|everyone gets .* wrong|upside down|surprised me|"
    r"the truth|lied to)", re.I)


def extract_title_flags(title: str) -> Dict[str, bool]:
    return {
        "title.identity": bool(_IDENTITY.search(title)),
        "title.first_person": bool(_FIRST_PERSON.search(title)),
        "title.specific_system": bool(_SPECIFIC.search(title)),
        "title.curiosity_gap": bool(_CURIOSITY.search(title)),
        "title.number_list": bool(re.search(r"\d", title)),
        "title.fear_clickbait": bool(_FEAR.search(title)
                                     or re.search(r"\b[A-Z]{3,}\b", title)),
    }


def extract_hook_flags(hook: str) -> Dict[str, bool]:
    return {
        "hook.polarizing": bool(_POLARIZING.search(hook)),
        "hook.fear": bool(_FEAR_HOOK.search(hook)),
    }


def extract_thumb_flags(features: Dict) -> Dict[str, bool]:
    emotion = str(features.get("emotion", "")).lower()
    return {
        "thumb.face": int(features.get("faces", 0)) > 0,
        "thumb.clean": bool(features.get("clean")),
        "thumb.text_overlay": bool(str(features.get("text_overlay", "")).strip()),
        "thumb.expressive": emotion in {"shock", "intense"},
    }


def analyze(video: Video) -> Video:
    flags: Dict[str, bool] = {}
    flags.update(extract_title_flags(video.title))
    flags.update(extract_hook_flags(video.hook))
    flags.update(extract_thumb_flags(video.thumbnail_features))
    video.feature_flags = flags
    video.analysis = {"present_features": [k for k, v in flags.items() if v],
                      "title_len_words": len(video.title.split())}
    return video


def analyze_corpus(videos: List[Video]) -> List[Video]:
    return [analyze(v) for v in videos]
