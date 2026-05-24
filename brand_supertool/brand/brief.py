"""Content brief generator — niche-agnostic.

Input: a topic + the niche's surviving patterns.
Output: 3 titles, thumbnail direction, hook, caption structure — every line
grounded in a SURVIVING pattern and filtered through the niche's brand.

Uses Claude when available; otherwise a deterministic generator that always
produces usable, on-brand output.
"""
from __future__ import annotations

from typing import List

from .. import config, llm
from ..models import ContentBrief, PatternClaim
from .filter import anti_pattern_flags, brand_alignment, translate_pattern


def _survivor_features(survivors: List[PatternClaim]) -> set:
    return {c.feature for c in survivors if translate_pattern(c)[1]}


def _persona_word(niche: dict) -> str:
    p = niche.get("persona", "creator")
    return p if len(p.split()) <= 2 else "creator"


def _titles(topic: str, feats: set, niche: dict) -> List[str]:
    t = topic.strip().rstrip(".")
    T = t[0].upper() + t[1:] if t else t
    persona = _persona_word(niche)
    pillar = (niche.get("pillars") or ["results"])[0]
    out: List[str] = []
    if "title.identity" in feats:
        out.append(f"Become the Person Who Actually Masters {T}")
    if "title.first_person" in feats:
        out.append(f"I Tried {T} for 30 Days — Here's What Actually Happened")
    if "title.specific_system" in feats:
        out.append(f"The {T} System That Actually Works (Step by Step)")
    if "title.curiosity_gap" in feats:
        out.append(f"The Truth About {T} Nobody Tells You")
    defaults = [
        f"{T}: The {pillar.title()} Approach",
        f"How I Think About {T} as a {persona.title()}",
        f"The Honest Guide to {T}",
    ]
    for d in defaults:
        if len(out) >= 3:
            break
        if d not in out:
            out.append(d)
    return out[:3]


def _thumb(feats: set) -> str:
    bits = []
    if "thumb.face" in feats:
        bits.append("your face in frame, calm and expressive")
    if "thumb.clean" in feats:
        bits.append("one clear subject with lots of empty space")
    if not bits:
        bits = ["one clear subject, high contrast, minimal clutter"]
    return "; ".join(bits) + ". Keep text overlay minimal or none."


def generate_brief(topic: str, survivors: List[PatternClaim],
                   niche_key: str = config.DEFAULT_NICHE) -> ContentBrief:
    niche = config.NICHES.get(niche_key, config.NICHES[config.DEFAULT_NICHE])
    brand = config.get_brand(niche_key)
    grounded = [c.feature for c in survivors if translate_pattern(c)[1]]

    if llm.available():
        system = (
            f"You are a content strategist for a {niche['label']} creator. "
            f"Voice: {', '.join(niche['tone'])}. Pillars: {', '.join(niche['pillars'])}. "
            f"NEVER use: {', '.join(niche['anti_patterns'])}."
        )
        patt = "\n".join(f"- {c.statement} (robustness {c.robustness})"
                         for c in survivors[:8])
        prompt = (
            f"Topic: {topic}\n\nProven niche patterns (validated):\n{patt}\n\n"
            "Return JSON with keys: titles (array of 3), thumbnail_direction, "
            "hook (first 3 seconds), caption_structure, rationale."
        )
        data = llm.complete_json(prompt, system=system, max_tokens=900)
        if isinstance(data, dict) and data.get("titles"):
            brief = ContentBrief(
                topic=topic, titles=list(data["titles"])[:3],
                thumbnail_direction=str(data.get("thumbnail_direction", "")),
                hook=str(data.get("hook", "")),
                caption_structure=str(data.get("caption_structure", "")),
                rationale=str(data.get("rationale", "")), grounded_in=grounded)
            _finalize(brief, brand)
            return brief

    feats = _survivor_features(survivors)
    titles = _titles(topic, feats, niche)
    hook = (f"Everything you've been told about {topic.lower().rstrip('.')} "
            "misses the real point. Here's what actually works.")
    caption = (
        "1) Open with the identity or outcome the viewer wants.\n"
        "2) Your lived proof or the specific method — be concrete.\n"
        "3) The one principle they can apply today.\n"
        "4) A grounded invitation. Invite, don't sell — no pushy CTA."
    )
    rationale = "Grounded in surviving patterns: " + (
        ", ".join(grounded) if grounded else "brand defaults (no patterns survived)")
    brief = ContentBrief(
        topic=topic, titles=titles, thumbnail_direction=_thumb(feats),
        hook=hook, caption_structure=caption, rationale=rationale,
        grounded_in=grounded)
    _finalize(brief, brand)
    return brief


def _finalize(brief: ContentBrief, brand) -> None:
    blob = " ".join(brief.titles) + " " + brief.hook + " " + brief.caption_structure
    brief.brand_alignment = brand_alignment(blob, brand)
    brief.anti_pattern_flags = anti_pattern_flags(blob, brand)
