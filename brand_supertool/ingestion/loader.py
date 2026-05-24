"""Chooses the data source per niche: live YouTube API when channel IDs +
a key exist, else the synthesized sample corpus for that niche."""
from __future__ import annotations

from typing import List

from .. import config
from ..models import Video
from .sample_data import sample_videos


def load_videos(niche_key: str = config.DEFAULT_NICHE,
                force_sample: bool = False) -> List[Video]:
    """Return the corpus of videos to analyze for a niche.

    Live mode requires a YOUTUBE_API_KEY *and* the niche to define creator
    channel_ids. Otherwise (and on any live failure) we use the sample corpus.
    """
    niche = config.NICHES.get(niche_key, config.NICHES[config.DEFAULT_NICHE])
    channels = [c for c in niche.get("creator_channels", []) if c]
    if force_sample or not config.YOUTUBE_API_KEY or not channels:
        return sample_videos(niche_key)

    try:
        from .youtube import YouTubeClient
        client = YouTubeClient(config.YOUTUBE_API_KEY)
        videos: List[Video] = []
        for ch in channels:
            vids = client.top_videos(ch["channel_id"], ch["name"],
                                     config.TOP_VIDEOS_PER_CREATOR)
            for v in vids:
                v.top_comments = client.top_comments(v.id)
            videos.extend(vids)
        return videos or sample_videos(niche_key)
    except Exception as exc:  # never hard-fail
        print(f"[loader] live fetch failed ({exc}); using sample corpus")
        return sample_videos(niche_key)
