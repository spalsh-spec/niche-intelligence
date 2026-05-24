"""Configuration: the niche registry + runtime settings.

The tool now serves ANY creator. Each niche below is a self-contained brand
profile (pillars / tone / anti-patterns / persona / sample topics). Pick a niche
at runtime (CLI --niche, or the web-app picker) and the whole pipeline retargets.

Add your own niche by copying one block. No other code changes required.
"""
from __future__ import annotations

import os
from pathlib import Path

from .models import BrandProfile

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(os.getenv("BST_OUTPUT_DIR", ROOT / "output"))

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

# Analysis tuning knobs (shared across niches)
TOP_VIDEOS_PER_CREATOR = 10
REPORT_TOP_N = 10
MIN_ROBUSTNESS = 0.5
MIN_SUPPORT = 3
MIN_LIFT = 1.15

LIVE_MODE = bool(YOUTUBE_API_KEY)
LLM_MODE = bool(ANTHROPIC_API_KEY)

# --------------------------------------------------------------------------- #
# THE NICHE REGISTRY — the "marketplace" of creator types.
# persona = the aspirational identity the audience wants to become.
# topics  = seed subjects used to synthesize a realistic sample corpus.
# --------------------------------------------------------------------------- #
NICHES = {
    "fitness": {
        "label": "Fitness", "emoji": "🏋️", "persona": "athlete",
        "tagline": "Strength, energy, and a body you've earned.",
        "pillars": ["discipline", "energy", "strength", "longevity", "movement", "aesthetics"],
        "tone": ["direct", "motivating", "grounded"],
        "anti_patterns": ["fear-based clickbait", "crash diet", "get shredded quick"],
        "audience": "People who want a strong, capable body and a routine that lasts.",
        "topics": ["fat loss", "building muscle", "morning routine", "mobility", "high protein eating", "fasted training"],
        "creators": ["Iron Ethos", "The Lean Method", "Daily Discipline", "Movement First", "Peak Form", "Strong & Simple"],
    },
    "finance": {
        "label": "Finance", "emoji": "📈", "persona": "investor",
        "tagline": "Build wealth without the hype.",
        "pillars": ["wealth", "freedom", "discipline", "compounding", "ownership", "calm"],
        "tone": ["clear", "credible", "no-hype"],
        "anti_patterns": ["fear-based clickbait", "get rich quick", "pump and dump"],
        "audience": "People who want financial independence through steady, sane decisions.",
        "topics": ["index funds", "paying off debt", "first 100k", "side income", "tax basics", "budgeting"],
        "creators": ["Calm Capital", "The Long Game", "Money Unhyped", "Compound Daily", "Plain Wealth", "Quiet Returns"],
    },
    "self-help": {
        "label": "Self-Help", "emoji": "🌱", "persona": "person you want to become",
        "tagline": "Become the version of you that follows through.",
        "pillars": ["discipline", "clarity", "confidence", "habits", "purpose", "calm"],
        "tone": ["warm", "direct", "grounded"],
        "anti_patterns": ["fear-based clickbait", "toxic hustle", "fake guru"],
        "audience": "People who want to change their life with habits that actually stick.",
        "topics": ["beating procrastination", "morning habits", "deep focus", "confidence", "discipline", "quitting your phone"],
        "creators": ["Quiet Progress", "The Follow-Through", "Become More", "Clear Mind", "Small Wins", "The Calm Build"],
    },
    "philosophy": {
        "label": "Philosophy", "emoji": "🏛️", "persona": "thinker",
        "tagline": "Old ideas for a clearer modern life.",
        "pillars": ["wisdom", "stoicism", "meaning", "clarity", "virtue", "calm"],
        "tone": ["thoughtful", "grounded", "calm"],
        "anti_patterns": ["fear-based clickbait", "shallow hot take", "rage bait"],
        "audience": "People seeking meaning and calm through timeless ideas.",
        "topics": ["stoicism", "dealing with death", "finding meaning", "the good life", "controlling anger", "memento mori"],
        "creators": ["The Examined Life", "Stoic & Sober", "Old Wisdom", "Think Slowly", "The Quiet Mind", "First Principles"],
    },
    "martial-arts": {
        "label": "Martial Arts", "emoji": "🥋", "persona": "fighter",
        "tagline": "Skill, composure, and respect under pressure.",
        "pillars": ["skill", "discipline", "composure", "respect", "courage", "mastery"],
        "tone": ["direct", "respectful", "intense"],
        "anti_patterns": ["fear-based clickbait", "fake black belt", "street-fight bait"],
        "audience": "People who train to be calm, capable, and dangerous-when-needed.",
        "topics": ["first sparring", "guard passing", "footwork", "staying calm under pressure", "conditioning", "self-defense basics"],
        "creators": ["Quiet Hands", "The Calm Fighter", "Mat Time", "Flow & Pressure", "Honest Grappler", "Composed Combat"],
    },
    "education": {
        "label": "Education", "emoji": "📚", "persona": "expert who can teach",
        "tagline": "Make hard things click.",
        "pillars": ["clarity", "mastery", "curiosity", "rigor", "simplicity", "depth"],
        "tone": ["clear", "patient", "engaging"],
        "anti_patterns": ["fear-based clickbait", "dumbed-down fluff", "exam-cram panic"],
        "audience": "Learners who want to truly understand, not just memorize.",
        "topics": ["learning faster", "explaining calculus", "study systems", "memory techniques", "first principles", "note-taking"],
        "creators": ["Make It Click", "The Clear Explainer", "Deep Understand", "Learn Honestly", "Mental Models", "The Patient Teacher"],
    },
    "fashion": {
        "label": "Fashion", "emoji": "🧥", "persona": "style icon",
        "tagline": "Dress like the person you're becoming.",
        "pillars": ["style", "identity", "confidence", "craft", "timelessness", "fit"],
        "tone": ["confident", "tasteful", "direct"],
        "anti_patterns": ["fear-based clickbait", "fast-fashion haul spam", "trend-chasing"],
        "audience": "People who want a personal style that signals who they are.",
        "topics": ["building a capsule wardrobe", "fit basics", "timeless pieces", "color theory", "dressing for your frame", "thrifting well"],
        "creators": ["The Cut & Cloth", "Quiet Style", "Well Dressed Man", "Timeless Fits", "Fabric First", "Effortless"],
    },
    "beauty": {
        "label": "Beauty", "emoji": "💄", "persona": "confident, glowing version of you",
        "tagline": "Skin and confidence, no gatekeeping.",
        "pillars": ["confidence", "skin health", "self-care", "authenticity", "simplicity", "glow"],
        "tone": ["warm", "honest", "encouraging"],
        "anti_patterns": ["fear-based clickbait", "miracle product hype", "insecurity bait"],
        "audience": "People who want real results and confidence, not insecurity-selling.",
        "topics": ["a simple skincare routine", "clearing acne", "natural makeup", "anti-aging basics", "glowing skin", "minimal beauty"],
        "creators": ["Bare & Honest", "The Skin Edit", "Glow Simply", "Real Routine", "Clean Confidence", "Quiet Beauty"],
    },
    "food": {
        "label": "Food & Cooking", "emoji": "🍳", "persona": "home cook",
        "tagline": "Real food, real skills, no stress.",
        "pillars": ["flavor", "simplicity", "skill", "nourishment", "joy", "craft"],
        "tone": ["warm", "practical", "inviting"],
        "anti_patterns": ["fear-based clickbait", "rage-bait recipe", "diet fear"],
        "audience": "People who want to cook confidently with simple, great food.",
        "topics": ["one-pan dinners", "knife skills", "perfect eggs", "meal prep", "cheap healthy meals", "cooking for beginners"],
        "creators": ["The Home Kitchen", "Simply Cooked", "Real Food Daily", "Knife & Flame", "Everyday Plates", "Cook Honest"],
    },
    "tech": {
        "label": "Tech & AI", "emoji": "💻", "persona": "builder",
        "tagline": "Build, ship, and stay ahead.",
        "pillars": ["building", "clarity", "leverage", "curiosity", "craft", "future"],
        "tone": ["sharp", "clear", "practical"],
        "anti_patterns": ["fear-based clickbait", "AI doom bait", "hype thread"],
        "audience": "People who want to build with tech and understand what matters.",
        "topics": ["building with AI", "your first app", "automating your workflow", "best dev tools", "learning to code", "AI agents"],
        "creators": ["Ship It", "The Build Log", "Clear Code", "Leverage AI", "Make & Ship", "Honest Tech"],
    },
    "gaming": {
        "label": "Gaming", "emoji": "🎮", "persona": "player who actually improves",
        "tagline": "Play sharper, climb faster.",
        "pillars": ["skill", "fun", "improvement", "community", "mastery", "flow"],
        "tone": ["energetic", "honest", "fun"],
        "anti_patterns": ["fear-based clickbait", "rage bait", "fake pro"],
        "audience": "Players who want to genuinely improve and enjoy it more.",
        "topics": ["ranking up fast", "aim training", "game sense", "the best settings", "mindset for tilt", "improving in a week"],
        "creators": ["Climb Calmly", "The Honest Gamer", "Game Sense", "Aim & Brain", "Rank Up Right", "Flow State"],
    },
    "engineering": {
        "label": "Engineering", "emoji": "⚙️", "persona": "engineer",
        "tagline": "Real systems, real reasoning.",
        "pillars": ["rigor", "clarity", "craft", "problem-solving", "depth", "simplicity"],
        "tone": ["precise", "clear", "grounded"],
        "anti_patterns": ["fear-based clickbait", "cargo-cult advice", "hype"],
        "audience": "Engineers who want depth and judgment, not buzzwords.",
        "topics": ["system design", "debugging like a pro", "clean architecture", "first principles", "trade-offs", "writing better code"],
        "creators": ["First Principles Eng", "The Clear System", "Honest Engineer", "Design & Trade-offs", "Deep Build", "Simple Systems"],
    },
    "vlogging": {
        "label": "Vlogging", "emoji": "🎥", "persona": "creator people root for",
        "tagline": "A life worth filming, told well.",
        "pillars": ["story", "authenticity", "energy", "connection", "craft", "consistency"],
        "tone": ["warm", "honest", "energetic"],
        "anti_patterns": ["fear-based clickbait", "fake drama", "rage bait"],
        "audience": "People building an audience around a real, magnetic life.",
        "topics": ["telling a better story", "a day in my life", "filming on a phone", "growing from zero", "editing for retention", "finding your voice"],
        "creators": ["The Honest Lens", "Real Days", "Story First", "Quiet Camera", "Live & Film", "The Build in Public"],
    },
    "branding": {
        "label": "Branding", "emoji": "✦", "persona": "brand people remember",
        "tagline": "Be the name people remember.",
        "pillars": ["identity", "clarity", "trust", "consistency", "story", "distinctiveness"],
        "tone": ["sharp", "confident", "clear"],
        "anti_patterns": ["fear-based clickbait", "follow-for-follow", "vanity-metric bait"],
        "audience": "Founders and creators building a brand that compounds trust.",
        "topics": ["finding your positioning", "a memorable name", "building trust", "your brand voice", "standing out", "personal brand from zero"],
        "creators": ["The Clear Brand", "Memorable", "Trust Compounds", "Positioning First", "Distinct", "Quiet Authority"],
    },
}

DEFAULT_NICHE = "fitness"


def get_brand(niche_key: str = DEFAULT_NICHE) -> BrandProfile:
    n = NICHES.get(niche_key, NICHES[DEFAULT_NICHE])
    return BrandProfile(
        pillars=n["pillars"], tone=n["tone"],
        anti_patterns=n["anti_patterns"], audience_psychology=n["audience"],
    )


# Back-compat: a default BRAND (used by older callers / tests).
BRAND = get_brand(DEFAULT_NICHE)
