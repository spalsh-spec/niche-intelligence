"""Content brief generator.

Input: a topic/idea.
Output: 3 title options, thumbnail direction, 3-second hook, caption structure
        — every line grounded in a SURVIVING pattern and filtered through brand.

Uses Claude when available; otherwise a deterministic generator seeded by the
surviving patterns so it always produces something usable and on-brand.
"""
from __future__ import annotations

from typing import List

from .. import llm
from ..models import BrandProfile, ContentBrief, PatternClaim
from .filter import anti_pattern_flags, brand_alignment, translate_pattern


def _survivor_features(survivors: List[PatternClaim]) -> set:
    return {c.feature for c in survivors
            if translate_pattern(c)[1]}  # recommended only


def _heuristic_titles(topic: str, feats: set) -> List[str]:
    t = topic.strip().rstrip(".")
    titles: List[str] = []
    if "title.identity_trigger" in feats:
        titles.append(f"Become the Man Who Mastered {t.title()} (No App, No Scale)")
    if "title.first_person_result" in feats:
        titles.append(f"I Tried {t.title()} for 30 Days Eating Like a Greek Fisherman")
    if "title.freedom_negation" in feats:
        titles.append(f"{t.title()} — Without the Scale, the App, or the Gym")
    if "title.curiosity_gap" in feats:
        titles.append(f"The Truth About {t.title()} Nobody in the Gym Will Tell You")
    # guarantee 3, on-brand defaults
    defaults = [
        f"{t.title()} the Mediterranean Way",
        f"How I Stay Lean Year-Round: {t.title()} in the Sun",
        f"The Old-World Approach to {t.title()}",
    ]
    for d in defaults:
        if len(titles) >= 3:
            break
        if d not in titles:
            titles.append(d)
    return titles[:3]


def _heuristic_thumb(feats: set) -> str:
    bits = []
    if "thumb.outdoor" in feats:
        bits.append("outdoor coast or mountain backdrop")
    if "thumb.sunlit" in feats:
        bits.append("warm low-angle sunlight")
    if "thumb.shirtless" in feats:
        bits.append("natural earned physique (not posed)")
    if "thumb.face" in feats:
        bits.append("calm stoic face in frame")
    if not bits:
        bits = ["outdoor, sunlit, grounded — old-world living, no gym wall"]
    return "; ".join(bits) + ". Keep text overlay minimal or none."


def generate_brief(topic: str, survivors: List[PatternClaim],
                   brand: BrandProfile) -> ContentBrief:
    grounded = [c.feature for c in survivors if translate_pattern(c)[1]]

    # ---- try Claude first ----
    if llm.available():
        system = (
            "You are a content strategist for a Mediterranean-lifestyle, "
            "holistic-fitness creator. Voice: direct, masculine, free-spirited, "
            "grounded. NEVER reference calorie counting, macro tracking, "
            "gym-bro aesthetics, hustle culture, or fear-based clickbait."
        )
        patt = "\n".join(f"- {c.statement} (robustness {c.robustness})"
                         for c in survivors[:8])
        prompt = (
            f"Topic: {topic}\n\nProven niche patterns (already validated):\n{patt}\n\n"
            "Produce a content brief as JSON with keys: titles (array of 3), "
            "thumbnail_direction (string), hook (string, first 3 seconds), "
            "caption_structure (string), rationale (string)."
        )
        data = llm.complete_json(prompt, system=system, max_tokens=900)
        if isinstance(data, dict) and data.get("titles"):
            brief = ContentBrief(
                topic=topic,
                titles=list(data["titles"])[:3],
                thumbnail_direction=str(data.get("thumbnail_direction", "")),
                hook=str(data.get("hook", "")),
                caption_structure=str(data.get("caption_structure", "")),
                rationale=str(data.get("rationale", "")),
                grounded_in=grounded,
            )
            _finalize(brief, brand)
            return brief

    # ---- deterministic fallback ----
    feats = _survivor_features(survivors)
    titles = _heuristic_titles(topic, feats)
    hook = ("Everything you were told about " + topic.lower().rstrip(".")
            + " is upside down. Here's the old-world way.")
    caption = (
        "1) Polarizing one-liner that names the identity.\n"
        "2) The lived proof (what you did, no tracking).\n"
        "3) The simple principle the audience can copy today.\n"
        "4) One line of freedom/aspiration. Invite, don't sell — no pushy CTA."
    )
    rationale = "Grounded in surviving patterns: " + (
        ", ".join(grounded) if grounded else "brand defaults (no patterns survived)")
    brief = ContentBrief(
        topic=topic, titles=titles, thumbnail_direction=_heuristic_thumb(feats),
        hook=hook, caption_structure=caption, rationale=rationale,
        grounded_in=grounded,
    )
    _finalize(brief, brand)
    return brief


def _finalize(brief: ContentBrief, brand: BrandProfile) -> None:
    blob = " ".join(brief.titles) + " " + brief.hook + " " + brief.caption_structure
    brief.brand_alignment = brand_alignment(blob, brand)
    brief.anti_pattern_flags = anti_pattern_flags(blob, brand)
