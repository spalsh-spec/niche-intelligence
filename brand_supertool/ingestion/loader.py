"""Chooses the data source: live YouTube API when a key exists, else sample."""
from __future__ import annotations

from typing import List

from .. import config
from ..models import Video
from .sample_data import sample_videos


def load_videos(force_sample: bool = False) -> List[Video]:
    """Return the corpus of videos to analyze.

    Live mode is attempted only when a key is present and force_sample is off.
    Any live failure degrades gracefully to the sample corpus so the pipeline
    never hard-fails on a flaky network.
    """
    if force_sample or not config.YOUTUBE_API_KEY:
        return sample_videos()

    try:
        from .youtube import YouTubeClient
        client = YouTubeClient(config.YOUTUBE_API_KEY)
        videos: List[Video] = []
        for creator in config.TRACKED_CREATORS:
            if creator.get("platform") != "youtube":
                continue
            vids = client.top_videos(
                creator["channel_id"], creator["name"],
                config.TOP_VIDEOS_PER_CREATOR,
            )
            for v in vids:
                v.top_comments = client.top_comments(v.id)
            videos.extend(vids)
        return videos or sample_videos()
    except Exception as exc:  # network/quota/key issues -> never crash
        print(f"[loader] live fetch failed ({exc}); using sample corpus")
        return sample_videos()
