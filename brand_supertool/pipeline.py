"""End-to-end orchestration: the four layers wired together.

    ingest -> analyze -> fuzzy score -> mine patterns -> falsify -> bundle

Returns a plain dict (`Insight` bundle) that the reporting + brief layers
consume. Deterministic given the same corpus.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from . import config
from .intelligence import falsify, fuzzy, patterns
from .intelligence.analyzer import analyze_corpus
from .ingestion import load_videos
from .models import PatternClaim, Video


@dataclass
class Insight:
    videos: List[Video]                       # scored + analyzed, desc by score
    survivors: List[PatternClaim] = field(default_factory=list)
    all_claims: List[PatternClaim] = field(default_factory=list)
    live_mode: bool = False
    llm_mode: bool = False

    @property
    def top(self) -> List[Video]:
        return self.videos[:config.REPORT_TOP_N]


def run(force_sample: bool = False) -> Insight:
    videos = load_videos(force_sample=force_sample)
    analyze_corpus(videos)          # sets feature_flags
    fuzzy.score_corpus(videos)      # sets performance_score (also sorts desc)

    platforms = {v.platform for v in videos}
    survivors: List[PatternClaim] = []
    all_claims: List[PatternClaim] = []
    for plat in platforms:
        claims = patterns.mine_patterns(videos, platform=plat)
        surv, evaluated = falsify.evaluate_all(claims, videos)
        survivors += surv
        all_claims += evaluated

    survivors.sort(key=lambda c: c.robustness, reverse=True)
    return Insight(
        videos=videos, survivors=survivors, all_claims=all_claims,
        live_mode=config.LIVE_MODE and not force_sample,
        llm_mode=config.LLM_MODE,
    )
