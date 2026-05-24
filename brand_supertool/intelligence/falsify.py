"""Falsification eval — Popper, applied to content patterns.

A correlation is not knowledge. Before the tool tells you "identity titles win",
it actively tries to PROVE THAT CLAIM WRONG and reports how badly it failed to.

For a claim "feature F is associated with above-average performance":

  counterexample : a video that HAS F but still underperformed
                   (F present, prediction failed)
  contradiction  : a video that WON WITHOUT F
                   (F not necessary -> weakens the explanation)

  falsification_ratio = 0.6 * counterexample_rate + 0.4 * contradiction_rate
                        (0 = unfalsified / bulletproof, 1 = fully falsified)

  robustness = (1 - falsification_ratio) * effect_factor
               where effect_factor discounts claims with a trivial lift.

Only claims that survive (robustness >= MIN_ROBUSTNESS, enough support, real
lift) are allowed into the report. This is the firewall between "the AI noticed
a correlation" and "this is actually true".
"""
from __future__ import annotations

from typing import List, Tuple

from .. import config
from ..models import PatternClaim, Video


def _winner_threshold(videos: List[Video]) -> float:
    scores = [v.performance_score for v in videos]
    return sum(scores) / len(scores) if scores else 0.0


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def evaluate_claim(claim: PatternClaim, videos: List[Video],
                   threshold: float) -> PatternClaim:
    corpus = [v for v in videos if v.platform == claim.platform]
    has = [v for v in corpus if v.feature_flags.get(claim.feature)]
    lacks = [v for v in corpus if not v.feature_flags.get(claim.feature)]
    winners = [v for v in corpus if v.performance_score >= threshold]

    positive = claim.lift >= 1.0

    if positive:
        counterexamples = [v for v in has if v.performance_score < threshold]
        contradictions = [v for v in winners
                          if not v.feature_flags.get(claim.feature)]
    else:
        # claim says F hurts -> challenged by F-videos that won anyway
        counterexamples = [v for v in has if v.performance_score >= threshold]
        losers = [v for v in corpus if v.performance_score < threshold]
        contradictions = [v for v in losers
                          if not v.feature_flags.get(claim.feature)]

    counter_rate = len(counterexamples) / len(has) if has else 1.0
    contra_base = winners if positive else [v for v in corpus
                                            if v.performance_score < threshold]
    contra_rate = len(contradictions) / len(contra_base) if contra_base else 1.0

    falsification = 0.6 * counter_rate + 0.4 * contra_rate
    effect = _clamp(abs(claim.lift - 1.0) / 0.5, 0.3, 1.0)
    robustness = (1.0 - falsification) * effect

    claim.counterexamples = len(counterexamples)
    claim.contradictions = len(contradictions)
    claim.falsification_ratio = round(falsification, 3)
    claim.robustness = round(robustness, 3)

    enough_support = claim.support >= config.MIN_SUPPORT
    real_lift = (claim.lift >= config.MIN_LIFT) if positive \
        else (claim.lift <= 1.0 / config.MIN_LIFT)
    claim.survived = (robustness >= config.MIN_ROBUSTNESS
                      and enough_support and real_lift)

    if claim.survived:
        claim.verdict = "supported"
    elif falsification >= 0.5 or not real_lift:
        claim.verdict = "falsified"
    else:
        claim.verdict = "weak"
    return claim


def evaluate_all(claims: List[PatternClaim],
                 videos: List[Video]) -> Tuple[List[PatternClaim], List[PatternClaim]]:
    """Returns (survivors, all_evaluated). Survivors sorted by robustness."""
    if not claims:
        return [], []
    threshold = _winner_threshold(
        [v for v in videos if v.platform == claims[0].platform])
    evaluated = [evaluate_claim(c, videos, threshold) for c in claims]
    survivors = sorted([c for c in evaluated if c.survived],
                       key=lambda c: c.robustness, reverse=True)
    return survivors, evaluated
