"""Realistic Mediterranean-niche sample corpus.

Lets the whole pipeline run end-to-end with zero API keys. The data is
hand-tuned so that real, separable signal exists:

  * IDENTITY-TRIGGER titles genuinely overperform   -> should SURVIVE falsify
  * "number in title" is deliberately noisy          -> should be WEAKENED
  * shirtless / outdoor / sunlit thumbnails win       -> should SURVIVE
  * fear/clickbait hooks underperform in this niche   -> negative signal

Counter-examples are baked in on purpose so the falsification eval has real
work to do rather than rubber-stamping every correlation.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from ..models import Video

_NOW = datetime(2026, 5, 24, tzinfo=timezone.utc)


def _d(days_ago: int) -> datetime:
    return _NOW - timedelta(days=days_ago)


# (creator, title, days_ago, views, likes, comments, hook, thumb, comments_list, tags)
_RAW = [
    # ---- Costa Vita ----
    ("Costa Vita",
     "I Got Leaner Eating Like a Greek Fisherman (No App, No Scale)",
     6, 412000, 38500, 2210,
     "Everything you were told about getting lean is upside down.",
     {"faces": 1, "emotion": "calm", "text_overlay": "NO SCALE", "setting": "outdoor-coast", "shirtless": True, "sunlit": True},
     ["This is the identity i want", "Bro the fisherman lifestyle is the dream",
      "Finally someone who isn't counting macros", "Where in Greece is this"],
     ["mediterranean", "fat loss", "lifestyle"]),
    ("Costa Vita",
     "The Olive Oil Protocol That Replaced My Supplements",
     13, 198000, 15600, 940,
     "I threw out every supplement I owned. Here's what happened.",
     {"faces": 1, "emotion": "calm", "text_overlay": "", "setting": "kitchen", "shirtless": False, "sunlit": True},
     ["love the simplicity", "olive oil gang", "what brand of oil"],
     ["holistic", "nutrition"]),
    ("Costa Vita",
     "5 Mistakes Killing Your Energy in 2026",
     9, 74000, 3100, 410,
     "Number 3 is destroying your testosterone.",
     {"faces": 1, "emotion": "shock", "text_overlay": "MISTAKE #3", "setting": "studio", "shirtless": False, "sunlit": False},
     ["clickbaity but ok", "number 3 wasn't even real", "meh"],
     ["energy", "listicle"]),

    # ---- The Stoic Lean ----
    ("The Stoic Lean",
     "Become the Man Who Doesn't Need the Gym Mirror",
     4, 356000, 41200, 3050,
     "Discipline isn't punishment. It's how free men live.",
     {"faces": 1, "emotion": "stoic", "text_overlay": "", "setting": "outdoor-mountain", "shirtless": True, "sunlit": True},
     ["this hit different", "the man i want to be", "stoicism + lifting finally",
      "saving this one"],
     ["stoicism", "identity", "mindset"]),
    ("The Stoic Lean",
     "Why I Train Fasted in the Morning Sun",
     17, 142000, 12900, 760,
     "The sun is a performance enhancer nobody talks about.",
     {"faces": 1, "emotion": "calm", "text_overlay": "", "setting": "outdoor-beach", "shirtless": True, "sunlit": True},
     ["sun energy is real", "morning sun changed me", "circadian gang"],
     ["sun", "training", "holistic"]),
    ("The Stoic Lean",
     "7 Stoic Rules for a Lean Body",
     11, 61000, 2400, 300,
     "Marcus Aurelius would never count a calorie.",
     {"faces": 0, "emotion": "neutral", "text_overlay": "7 RULES", "setting": "graphic", "shirtless": False, "sunlit": False},
     ["bit listy", "rule 4 good though", "ok"],
     ["stoicism", "listicle"]),

    # ---- Aegean Body ----
    ("Aegean Body",
     "Eat Like You Live by the Sea (Full Day of Eating)",
     5, 287000, 24100, 1510,
     "No tracking. No stress. Just real food and salt air.",
     {"faces": 1, "emotion": "calm", "text_overlay": "", "setting": "outdoor-coast", "shirtless": True, "sunlit": True},
     ["the vibe is unmatched", "this is freedom", "moving to the coast fr"],
     ["mediterranean", "diet", "lifestyle"]),
    ("Aegean Body",
     "The Truth About Protein Nobody in the Gym Will Tell You",
     8, 121000, 8800, 690,
     "You've been lied to about how much protein you need.",
     {"faces": 1, "emotion": "serious", "text_overlay": "THE TRUTH", "setting": "studio", "shirtless": False, "sunlit": False},
     ["curious now", "is this true", "source?"],
     ["nutrition", "curiosity"]),
    ("Aegean Body",
     "3 Reasons Your Diet Feels Like a Prison",
     20, 54000, 3900, 250,
     "Freedom starts on your plate.",
     {"faces": 1, "emotion": "calm", "text_overlay": "", "setting": "outdoor-garden", "shirtless": False, "sunlit": True},
     ["freedom is the word", "felt this", "the prison analogy"],
     ["freedom", "diet", "listicle"]),

    # ---- Sol & Iron ----
    ("Sol & Iron",
     "Train Like a Greek God Without a Single Machine",
     3, 398000, 36700, 2480,
     "The body you want was built on beaches, not in gyms.",
     {"faces": 1, "emotion": "intense", "text_overlay": "", "setting": "outdoor-beach", "shirtless": True, "sunlit": True},
     ["greek god physique goals", "beach training > gym", "this is the way"],
     ["calisthenics", "identity", "sun"]),
    ("Sol & Iron",
     "I Quit the Gym for 90 Days. Here's My Body Now.",
     14, 233000, 19800, 1320,
     "Ninety days, zero gym, one surprising result.",
     {"faces": 1, "emotion": "confident", "text_overlay": "90 DAYS", "setting": "outdoor-coast", "shirtless": True, "sunlit": True},
     ["the experiment we needed", "results speak", "90 day club"],
     ["experiment", "calisthenics"]),
    ("Sol & Iron",
     "Best 6 Supplements for Lean Muscle (Honest Review)",
     10, 38000, 1400, 180,
     "I tested every popular supplement so you don't have to.",
     {"faces": 0, "emotion": "neutral", "text_overlay": "TOP 6", "setting": "studio", "shirtless": False, "sunlit": False},
     ["too salesy", "supplement spam", "unsub"],
     ["supplements", "review"]),

    # ---- Olive Coast Athletic ----
    ("Olive Coast Athletic",
     "The Man You Become When You Stop Counting Calories",
     7, 312000, 33400, 2090,
     "Counting calories made me weak. Letting go made me strong.",
     {"faces": 1, "emotion": "stoic", "text_overlay": "", "setting": "outdoor-mountain", "shirtless": True, "sunlit": True},
     ["identity shift right here", "stopped tracking, never looked back",
      "the freedom is real"],
     ["identity", "fat loss", "freedom"]),
    ("Olive Coast Athletic",
     "A Day of Sun, Sea, and Strength in Crete",
     16, 176000, 16200, 880,
     "This is what holistic strength actually looks like.",
     {"faces": 1, "emotion": "calm", "text_overlay": "", "setting": "outdoor-coast", "shirtless": True, "sunlit": True},
     ["crete looks unreal", "sun sea strength", "the dream life"],
     ["travel", "sun", "lifestyle"]),
    ("Olive Coast Athletic",
     "10 Foods I Eat Every Week to Stay Lean Year-Round",
     12, 88000, 5200, 360,
     "Simple foods, no measuring, year-round leanness.",
     {"faces": 1, "emotion": "calm", "text_overlay": "10 FOODS", "setting": "kitchen", "shirtless": False, "sunlit": True},
     ["useful list", "food 7 surprised me", "saving"],
     ["nutrition", "listicle"]),

    # ---- Free Range Strong ----
    ("Free Range Strong",
     "Why Modern Men Feel Weak (And the Old-World Fix)",
     5, 341000, 35900, 2670,
     "We traded the sun and the sea for screens and stress.",
     {"faces": 1, "emotion": "serious", "text_overlay": "", "setting": "outdoor-field", "shirtless": True, "sunlit": True},
     ["the old world fix", "this is the identity", "modern life made us soft"],
     ["identity", "holistic", "mindset"]),
    ("Free Range Strong",
     "I Ate the Mediterranean Way for 30 Days (Body Update)",
     18, 207000, 17400, 1010,
     "Thirty days of olives, fish, and sun. Real results.",
     {"faces": 1, "emotion": "confident", "text_overlay": "30 DAYS", "setting": "outdoor-coast", "shirtless": True, "sunlit": True},
     ["the mediterranean way wins", "30 day results", "doing this"],
     ["mediterranean", "experiment"]),
    ("Free Range Strong",
     "STOP Doing These 8 Things Before Breakfast",
     9, 47000, 1900, 230,
     "You're sabotaging your whole day before 9am.",
     {"faces": 1, "emotion": "shock", "text_overlay": "STOP!", "setting": "studio", "shirtless": False, "sunlit": False},
     ["fear mongering", "the STOP titles are tired", "ok boomer"],
     ["routine", "clickbait", "listicle"]),
]


def sample_videos() -> List[Video]:
    vids: List[Video] = []
    for i, (creator, title, days, views, likes, comments, hook, thumb,
            top_comments, tags) in enumerate(_RAW):
        vids.append(Video(
            id=f"sample_{i:03d}",
            creator=creator,
            platform="youtube",
            title=title,
            url=f"https://youtube.com/watch?v=sample_{i:03d}",
            published_at=_d(days),
            views=views,
            likes=likes,
            comments=comments,
            hook=hook,
            thumbnail_features=thumb,
            thumbnail_url=f"https://i.ytimg.com/vi/sample_{i:03d}/hq.jpg",
            top_comments=top_comments,
            tags=tags,
        ))
    return vids
