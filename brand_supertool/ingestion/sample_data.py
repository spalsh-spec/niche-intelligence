"""Parametric sample corpus — synthesizes a realistic, analyzable dataset for
ANY niche from its registry definition (config.NICHES).

The signal design is deliberate and consistent across niches so the
falsification eval always has real work to do:

  WIN templates  (identity / first-person / specific system) -> high metrics
  NEUTRAL list   (generic "N tips")                          -> middling
  LOSE templates (fear clickbait / shallow curiosity bait)   -> low metrics

Two counter-examples are injected per niche (a win-pattern that flopped, a
list-pattern that overperformed) so robustness lands realistically below 1.0.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from .. import config
from ..models import Video

_NOW = datetime(2026, 5, 24, tzinfo=timezone.utc)


def _title(kind: str, topic: str) -> str:
    t = topic[0].upper() + topic[1:]
    return {
        "identity": f"Become the Person Who Mastered {t}",
        "firstperson": f"I Tried {t} for 30 Days — Here's What Happened",
        "specific": f"The {t} System That Actually Works (Step by Step)",
        "list": f"7 {t} Tips for Beginners",
        "fear": f"STOP Getting {t} Wrong Before It's Too Late",
        "curio": f"The Truth About {t} (You Won't Believe #3)",
    }[kind]


_HOOK = {
    "identity": "This is the identity shift nobody talks about.",
    "firstperson": "I documented everything. The results surprised me.",
    "specific": "Here's the exact system, step by step.",
    "list": "Quick wins you can use today.",
    "fear": "You're destroying your progress and don't even know it.",
    "curio": "Everyone gets this completely wrong.",
}

_THUMB = {
    "identity": {"faces": 1, "emotion": "calm", "text_overlay": "", "clean": True},
    "firstperson": {"faces": 1, "emotion": "curious", "text_overlay": "30 DAYS", "clean": True},
    "specific": {"faces": 1, "emotion": "calm", "text_overlay": "", "clean": True},
    "list": {"faces": 1, "emotion": "neutral", "text_overlay": "7 TIPS", "clean": True},
    "fear": {"faces": 1, "emotion": "shock", "text_overlay": "STOP!", "clean": False},
    "curio": {"faces": 1, "emotion": "shock", "text_overlay": "#3?!", "clean": False},
}

# base (views, like_rate, comment_rate) by kind
_BASE = {
    "identity": (360000, 0.105, 0.0075),
    "firstperson": (320000, 0.095, 0.0070),
    "specific": (300000, 0.100, 0.0072),
    "list": (105000, 0.055, 0.0042),
    "fear": (62000, 0.032, 0.0030),
    "curio": (70000, 0.035, 0.0032),
}


# 15 slots: each winning pattern appears 3x (clears MIN_SUPPORT), each weak 2x.
def sample_videos(niche_key: str = config.DEFAULT_NICHE) -> List[Video]:
    n = config.NICHES.get(niche_key, config.NICHES[config.DEFAULT_NICHE])
    topics, creators = n["topics"], n["creators"]
    rows = []  # [kind, topic, creator, days, scale]
    for kind in ("identity", "firstperson", "specific"):      # 9 winners
        for j in range(3):
            rows.append([kind, topics[j % len(topics)],
                         creators[len(rows) % len(creators)], 3 + len(rows), 1.0])
    for kind in ("list", "fear", "curio"):                    # 6 weaker
        for j in range(2):
            rows.append([kind, topics[(j + 3) % len(topics)],
                         creators[len(rows) % len(creators)], 3 + len(rows), 1.0])

    # --- inject counter-examples so falsification stays honest ---
    rows[8][4] = 0.18    # a 'specific' winner that flopped
    rows[9][4] = 3.0     # a 'list' (weak) that overperformed

    vids: List[Video] = []
    for idx, (kind, topic, creator, days, scale) in enumerate(rows):
        base_views, lr, cr = _BASE[kind]
        views = int(base_views * scale * (1 + 0.04 * ((idx % 5) - 2)))
        views = max(views, 8000)
        vids.append(Video(
            id=f"{niche_key}_{idx:03d}",
            creator=creator, platform="youtube",
            title=_title(kind, topic),
            url=f"https://youtube.com/watch?v={niche_key}_{idx:03d}",
            published_at=_NOW - timedelta(days=days),
            views=views, likes=int(views * lr), comments=int(views * cr),
            hook=_HOOK[kind],
            thumbnail_features=dict(_THUMB[kind]),
            thumbnail_url=f"https://i.ytimg.com/vi/{niche_key}_{idx:03d}/hq.jpg",
            top_comments=[], tags=[topic, niche_key],
        ))
    return vids
