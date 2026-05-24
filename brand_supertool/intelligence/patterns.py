"""Pattern mining — generate 'why it won' hypotheses.

For every content feature we split the corpus into HAS-feature vs LACKS-feature
and compare mean fuzzy performance. The output is a list of PatternClaim
*candidates*. They are explicitly untrusted until falsify.py stress-tests them.
"""
from __future__ import annotations

from typing import List

from ..models import PatternClaim, Video
from .analyzer import FEATURE_LABELS


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def mine_patterns(videos: List[Video], platform: str = "youtube") -> List[PatternClaim]:
    corpus = [v for v in videos if v.platform == platform]
    claims: List[PatternClaim] = []
    if not corpus:
        return claims

    for feature, label in FEATURE_LABELS.items():
        has = [v for v in corpus if v.feature_flags.get(feature)]
        lacks = [v for v in corpus if not v.feature_flags.get(feature)]
        if not has or not lacks:
            continue  # no contrast -> no claim possible

        avg_with = _mean([v.performance_score for v in has])
        avg_without = _mean([v.performance_score for v in lacks])
        lift = avg_with / avg_without if avg_without else 0.0
        direction = "outperform" if lift >= 1 else "underperform"

        examples = [v.title for v in sorted(
            has, key=lambda v: v.performance_score, reverse=True)[:3]]

        claims.append(PatternClaim(
            feature=feature,
            statement=f"Videos with {label} {direction} "
                      f"({avg_with:.0f} vs {avg_without:.0f} mean score).",
            platform=platform,
            support=len(has),
            population=len(corpus),
            avg_score_with=round(avg_with, 2),
            avg_score_without=round(avg_without, 2),
            lift=round(lift, 3),
            examples=examples,
        ))

    # strongest absolute effect first
    claims.sort(key=lambda c: abs(c.lift - 1.0), reverse=True)
    return claims
