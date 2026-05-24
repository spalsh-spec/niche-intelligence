"""Brand filter — score and flag any text against YOUR brand.

Two jobs:
  1. brand_alignment(text)  -> [0,1] how on-brand the copy is
  2. anti_pattern_flags(text) -> the off-brand things it tripped

Plus translate_pattern(): turns a (niche-wide) surviving pattern into guidance
phrased in your voice.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from ..models import BrandProfile, PatternClaim

_STOP = {"the", "a", "an", "of", "to", "and", "without", "your", "getting"}


def _keywords(phrases: List[str]) -> set:
    words = set()
    for p in phrases:
        for w in re.split(r"[^a-z]+", p.lower()):
            if w and w not in _STOP and len(w) > 2:
                words.add(w)
    return words


def anti_pattern_flags(text: str, brand: BrandProfile) -> List[str]:
    """An anti-pattern fires only when ALL its salient words appear — so an
    incidental single word never trips a false alarm."""
    text_l = text.lower()
    flags = []
    for ap in brand.anti_patterns:
        ap_words = [w for w in re.split(r"[^a-z]+", ap.lower())
                    if w and w not in _STOP and len(w) > 2]
        if ap_words and all(w in text_l for w in ap_words):
            flags.append(ap)
    return flags


def brand_alignment(text: str, brand: BrandProfile) -> float:
    text_l = text.lower()
    pillar_words = _keywords(brand.pillars)
    pillar_hits = sum(1 for w in pillar_words if w in text_l)
    anti_hits = len(anti_pattern_flags(text, brand))
    pillar_signal = min(pillar_hits / 2.0, 1.0)
    anti_signal = min(anti_hits / 1.0, 1.0)
    score = 0.5 + 0.5 * pillar_signal - 0.6 * anti_signal
    return round(max(0.0, min(1.0, score)), 3)


# Feature -> brand-flavored guidance. Niche-agnostic.
_BRAND_GUIDANCE = {
    "title.identity":
        "Lead with identity — name who the viewer becomes, not just what they "
        "learn. Aspiration outperforms information in almost every niche.",
    "title.first_person":
        "Frame it as lived proof ('I tried X for 30 days — here's what "
        "happened'). First-person reads as honesty, not a pitch.",
    "title.specific_system":
        "Promise a concrete system or step-by-step method. Specificity signals "
        "you actually know the path, not just the destination.",
    "title.curiosity_gap":
        "Open a real curiosity gap, but keep it true — 'the truth about X' "
        "only works when you actually deliver the truth. Never bait.",
    "thumb.face":
        "Put a calm, expressive face in frame. Human presence beats graphics.",
    "thumb.clean":
        "Keep the thumbnail clean and uncluttered — one subject, lots of air. "
        "Restraint reads as confidence.",
}

_BRAND_AVOID = {
    "title.fear_clickbait":
        "Skip it — fear/shouty clickbait spikes views but erodes the trust your "
        "brand compounds on. Off-brand wins cost more than they make.",
    "hook.fear":
        "Avoid fear-based hooks. Open with calm conviction, not panic.",
}


def translate_pattern(claim: PatternClaim) -> Tuple[str, bool]:
    """Return (brand guidance, is_recommended).

    is_recommended=False means 'this wins in the niche but is off-brand'.
    """
    if claim.feature in _BRAND_AVOID:
        return _BRAND_AVOID[claim.feature], False
    if claim.feature in _BRAND_GUIDANCE:
        return _BRAND_GUIDANCE[claim.feature], True
    return ("Apply this pattern in your own voice — stay true to your brand.", True)
