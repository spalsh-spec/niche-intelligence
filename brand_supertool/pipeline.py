"""End-to-end orchestration, per niche.

    ingest(niche) -> analyze -> fuzzy score -> mine patterns -> falsify -> bundle
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
    niche_key: str
    videos: List[Video]
    survivors: List[PatternClaim] = field(default_factory=list)
    all_claims: List[PatternClaim] = field(default_factory=list)
    live_mode: bool = False
    llm_mode: bool = False

    @property
    def top(self) -> List[Video]:
        return self.videos[:config.REPORT_TOP_N]


def run(niche_key: str = config.DEFAULT_NICHE,
        force_sample: bool = False) -> Insight:
    videos = load_videos(niche_key, force_sample=force_sample)
    analyze_corpus(videos)
    fuzzy.score_corpus(videos)

    survivors: List[PatternClaim] = []
    all_claims: List[PatternClaim] = []
    for plat in {v.platform for v in videos}:
        claims = patterns.mine_patterns(videos, platform=plat)
        surv, evaluated = falsify.evaluate_all(claims, videos)
        survivors += surv
        all_claims += evaluated

    survivors.sort(key=lambda c: c.robustness, reverse=True)
    return Insight(
        niche_key=niche_key, videos=videos, survivors=survivors,
        all_claims=all_claims,
        live_mode=config.LIVE_MODE and not force_sample,
        llm_mode=config.LLM_MODE)
