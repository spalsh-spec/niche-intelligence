"""Configuration: your brand, the creators you track, runtime settings.

This is the file you edit most. Everything that makes the tool *yours* lives
here. No code changes required to retarget it at a different niche.
"""
from __future__ import annotations

import os
from pathlib import Path

from .models import BrandProfile

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(os.getenv("BST_OUTPUT_DIR", ROOT / "output"))

# --------------------------------------------------------------------------- #
# API keys (optional — absence triggers sample-data / heuristic fallbacks)
# --------------------------------------------------------------------------- #
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
# Update if your account exposes a different string. Live mode only.
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

# --------------------------------------------------------------------------- #
# YOUR BRAND — the unique filter layer
# --------------------------------------------------------------------------- #
BRAND = BrandProfile(
    pillars=[
        "mediterranean lifestyle",
        "getting jacked without tracking",
        "freedom",
        "travel",
        "stoicism",
        "sun energy",
        "holistic health",
    ],
    tone=["direct", "masculine", "free-spirited", "grounded"],
    anti_patterns=[
        "calorie counting",
        "macro tracking",
        "gym-bro aesthetics",
        "hustle culture",
        "supplement spam",
        "fear-based clickbait",
    ],
    audience_psychology=(
        "Rejecting mainstream fitness culture. Seeking identity, not just "
        "information. Buying based on who they want to become — a leaner, "
        "freer, calmer version of themselves rooted in old-world living."
    ),
)

# --------------------------------------------------------------------------- #
# Creators you track. In live mode `channel_id` is used against the YouTube
# Data API. In sample mode only `name` matters.
# --------------------------------------------------------------------------- #
TRACKED_CREATORS = [
    {"name": "Costa Vita", "channel_id": "UC_SAMPLE_01", "platform": "youtube"},
    {"name": "The Stoic Lean", "channel_id": "UC_SAMPLE_02", "platform": "youtube"},
    {"name": "Aegean Body", "channel_id": "UC_SAMPLE_03", "platform": "youtube"},
    {"name": "Sol & Iron", "channel_id": "UC_SAMPLE_04", "platform": "youtube"},
    {"name": "Olive Coast Athletic", "channel_id": "UC_SAMPLE_05", "platform": "youtube"},
    {"name": "Free Range Strong", "channel_id": "UC_SAMPLE_06", "platform": "youtube"},
]

# --------------------------------------------------------------------------- #
# Analysis tuning knobs
# --------------------------------------------------------------------------- #
TOP_VIDEOS_PER_CREATOR = 10
REPORT_TOP_N = 10
# A pattern must survive the falsify eval with at least this robustness to be
# reported as actionable. Tightens the gap between "AI noticed something" and
# "this is real".
MIN_ROBUSTNESS = 0.5
MIN_SUPPORT = 3           # need at least N examples before we trust a pattern
MIN_LIFT = 1.15           # feature must beat the baseline by >=15%

LIVE_MODE = bool(YOUTUBE_API_KEY)
LLM_MODE = bool(ANTHROPIC_API_KEY)
