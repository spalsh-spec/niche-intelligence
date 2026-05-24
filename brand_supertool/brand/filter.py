"""Brand filter — score and flag any text against YOUR brand.

Two jobs:
  1. brand_alignment(text)  -> [0,1] how on-brand the copy is
  2. anti_pattern_flags(text) -> the off-brand things it tripped

Plus translate_pattern(): turns a (niche-wide) surviving pattern into guidance
phrased in your voice, e.g. a generic "identity titles win" becomes
"lead with who the viewer becomes — leaner, freer, sun-fed".
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
    incidental single word ('spam', 'culture') never trips a false alarm."""
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
    # Penalty is phrase-level for consistency with anti_pattern_flags: a lone
    # incidental keyword shouldn't tank alignment — only a full anti-pattern.
    anti_hits = len(anti_pattern_flags(text, brand))

    pillar_signal = min(pillar_hits / 2.0, 1.0)   # 2+ pillar words = full credit
    anti_signal = min(anti_hits / 1.0, 1.0)       # any full anti-pattern = penalty

    score = 0.5 + 0.5 * pillar_signal - 0.6 * anti_signal
    return round(max(0.0, min(1.0, score)), 3)


# Feature -> brand-flavored guidance (the "here's YOUR version" translation).
_BRAND_GUIDANCE = {
    "title.identity_trigger":
        "Lead with identity: name who the viewer becomes — leaner, freer, "
        "sun-fed, unbothered. Aspiration beats information in this niche.",
    "title.freedom_negation":
        "Make the freedom explicit — 'no scale', 'no app', 'no gym'. Your "
        "audience is actively rejecting tracking culture; reward that.",
    "title.first_person_result":
        "Frame as a lived experiment ('I ate like a Greek fisherman for 30 "
        "days'). First-person proof reads as honesty, not a pitch.",
    "title.curiosity_gap":
        "Open a curiosity gap, but keep it grounded and masculine — 'the "
        "olive-oil truth nobody in the gym will tell you', never fear-bait.",
    "thumb.shirtless":
        "Show the physique earned, not posed — natural light, real setting.",
    "thumb.sunlit":
        "Shoot in warm, low sun. Sun energy IS your brand; make the frame feel it.",
    "thumb.outdoor":
        "Get outside — coast, mountain, beach. Old-world living, not a gym wall.",
    "thumb.face":
        "Keep a calm, stoic face in frame. Presence over hype.",
}

# Patterns that, even if they 'win' niche-wide, you should NOT chase.
_BRAND_AVOID = {
    "title.fear_clickbait":
        "Skip it — fear/shouty clickbait violates the grounded, free-spirited "
        "tone even when it spikes views. Off-brand wins cost trust.",
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
    return ("Apply this pattern in your own voice — direct, masculine, "
            "grounded, free.", True)
