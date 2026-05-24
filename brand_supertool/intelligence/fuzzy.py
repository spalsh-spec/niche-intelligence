"""Fuzzy-logic performance scoring (Mamdani inference).

Why fuzzy and not a single weighted formula? Because "is this a winner?" is a
matter of degree, and the signals interact non-linearly. A video with merely
good velocity but explosive comment activity is a winner; a high-view video
that nobody engages with is not. Crisp thresholds ("> 100k views = winner")
throw away that nuance and behave badly at the boundaries.

Pipeline:
  raw signals -> rank-normalize to [0,1] (robust, corpus-relative)
              -> fuzzify into low / med / high
              -> apply rule base (min=AND, max=OR)
              -> aggregate output sets (max)
              -> defuzzify by centroid -> crisp score [0,100]

Pure Python, deterministic, no dependencies. Fully unit-tested.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

from ..models import Video

# --------------------------------------------------------------------------- #
# Membership function primitives
# --------------------------------------------------------------------------- #
def trimf(x: float, a: float, b: float, c: float) -> float:
    """Triangular membership."""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


def trapmf(x: float, a: float, b: float, c: float, d: float) -> float:
    """Trapezoidal membership."""
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (d - x) / (d - c)


# Input fuzzy sets over the normalized [0,1] universe.
def mf_low(x: float) -> float:
    return trapmf(x, -0.1, 0.0, 0.20, 0.45)


def mf_med(x: float) -> float:
    return trimf(x, 0.25, 0.5, 0.75)


def mf_high(x: float) -> float:
    return trapmf(x, 0.55, 0.80, 1.0, 1.1)


# Output singletons (Sugeno-style centroid) for the "winner" variable.
_OUT = {"low": 18.0, "med": 55.0, "high": 90.0}


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #
def _rank_norm(values: Sequence[float]) -> List[float]:
    """Percentile-rank normalization -> [0,1]. Robust to outliers/scale."""
    n = len(values)
    if n == 0:
        return []
    if n == 1:
        return [1.0]
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    for rank, idx in enumerate(order):
        ranks[idx] = rank / (n - 1)
    return ranks


# --------------------------------------------------------------------------- #
# Inference for one observation
# --------------------------------------------------------------------------- #
def infer(velocity: float, engagement: float, comments: float,
          likes: float) -> float:
    """Run the rule base on normalized signals; return crisp score [0,100]."""
    v_lo, v_md, v_hi = mf_low(velocity), mf_med(velocity), mf_high(velocity)
    e_lo, e_md, e_hi = mf_low(engagement), mf_med(engagement), mf_high(engagement)
    c_hi = mf_high(comments)
    l_hi = mf_high(likes)

    # rule strengths -> output sets
    strengths: Dict[str, float] = {"low": 0.0, "med": 0.0, "high": 0.0}

    def fire(out: str, strength: float) -> None:
        strengths[out] = max(strengths[out], strength)

    fire("high", min(v_hi, e_hi))                 # R1
    fire("high", min(v_hi, e_md))                 # R2
    fire("high", min(v_md, e_hi))                 # R3
    fire("high", c_hi)                            # R4: comment velocity is gold
    fire("med", min(v_md, e_md))                  # R5
    fire("med", min(l_hi, v_md))                  # R6
    fire("low", max(v_lo, e_lo))                  # R7: weak velocity OR weak eng

    num = sum(strengths[k] * _OUT[k] for k in strengths)
    den = sum(strengths.values())
    return num / den if den else 0.0


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def score_corpus(videos: List[Video]) -> List[Video]:
    """Compute derived signals + fuzzy performance_score for every video.

    Mutates and returns the list (sorted descending by score).
    """
    for v in videos:
        views = max(v.views, 1)
        v.engagement_rate = (v.likes + v.comments) / views
        v.comment_ratio = v.comments / views
        v.like_ratio = v.likes / views
        v.views_per_day = v.views / v.age_days()

    vel = _rank_norm([v.views_per_day for v in videos])
    eng = _rank_norm([v.engagement_rate for v in videos])
    com = _rank_norm([v.comment_ratio for v in videos])
    lik = _rank_norm([v.like_ratio for v in videos])

    for i, v in enumerate(videos):
        v.performance_score = round(infer(vel[i], eng[i], com[i], lik[i]), 2)
        v.winner_membership = round(v.performance_score / 100.0, 4)

    videos.sort(key=lambda v: v.performance_score, reverse=True)
    return videos
