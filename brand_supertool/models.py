"""Core data models shared across every layer.

Plain dataclasses, no external deps, so they serialize cleanly and are trivial
to test. Everything downstream (fuzzy scoring, falsify eval, brand filter,
reporting) speaks these types.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Video:
    """A single piece of content with its public performance signals."""

    id: str
    creator: str
    platform: str  # "youtube" | "instagram"
    title: str
    url: str
    published_at: datetime
    views: int
    likes: int
    comments: int
    # First line of caption / spoken hook (first 3s). Used by hook analysis.
    hook: str = ""
    # Pre-extracted thumbnail features (in sample mode) OR filled by vision in
    # live mode: {"faces": int, "emotion": str, "text_overlay": str,
    #             "dominant_colors": [..], "setting": str}
    thumbnail_features: Dict[str, Any] = field(default_factory=dict)
    thumbnail_url: str = ""
    top_comments: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # ---- derived signals (filled by the intelligence layer) ----
    engagement_rate: float = 0.0          # (likes + comments) / views
    comment_ratio: float = 0.0            # comments / views
    like_ratio: float = 0.0               # likes / views
    views_per_day: float = 0.0            # velocity since publish
    performance_score: float = 0.0        # crisp fuzzy output [0..100]
    winner_membership: float = 0.0        # fuzzy "is a winner" degree [0..1]
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    analysis: Dict[str, Any] = field(default_factory=dict)

    def age_days(self, now: Optional[datetime] = None) -> float:
        now = now or datetime.now(timezone.utc)
        published = self.published_at
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        delta = (now - published).total_seconds() / 86400.0
        return max(delta, 0.5)  # avoid divide-by-zero for brand-new posts

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["published_at"] = self.published_at.isoformat()
        return d


@dataclass
class PatternClaim:
    """A candidate 'why it won' hypothesis, e.g.

    "Titles with an identity trigger outperform."

    It is only trustworthy AFTER it survives the falsification eval.
    """

    feature: str                      # machine key, e.g. "title.identity_trigger"
    statement: str                    # human sentence
    platform: str
    support: int = 0                  # videos exhibiting the feature
    population: int = 0               # total videos considered
    avg_score_with: float = 0.0       # mean performance_score WITH feature
    avg_score_without: float = 0.0    # mean performance_score WITHOUT feature
    lift: float = 0.0                 # with / without
    # ---- filled by falsify.py ----
    counterexamples: int = 0          # has-feature-but-underperforms
    contradictions: int = 0           # lacks-feature-but-overperforms
    falsification_ratio: float = 1.0  # 0 = bulletproof, 1 = fully falsified
    robustness: float = 0.0           # [0..1] survives-falsification score
    survived: bool = False
    verdict: str = "unevaluated"      # "supported" | "weak" | "falsified"
    examples: List[str] = field(default_factory=list)  # winning video titles

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrandProfile:
    pillars: List[str]
    tone: List[str]
    anti_patterns: List[str]
    audience_psychology: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentBrief:
    topic: str
    titles: List[str]
    thumbnail_direction: str
    hook: str
    caption_structure: str
    rationale: str
    grounded_in: List[str] = field(default_factory=list)  # surviving pattern keys
    brand_alignment: float = 0.0
    anti_pattern_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
