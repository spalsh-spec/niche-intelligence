"""YouTube Data API v3 client.

Real implementation — drop a YOUTUBE_API_KEY into .env and it pulls live data.
Without a key the loader falls back to the bundled sample corpus, so nothing
here is mandatory to see the tool work.

Quota note: channels.list + playlistItems.list + videos.list per creator. The
free 10k/day quota comfortably covers a few dozen tracked creators daily.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - requests is optional for sample mode
    requests = None  # type: ignore

from ..models import Video

_API = "https://www.googleapis.com/youtube/v3"


class YouTubeClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("YouTubeClient requires an API key")
        if requests is None:
            raise RuntimeError("`requests` not installed; `pip install requests`")
        self.api_key = api_key

    # --- low-level ---------------------------------------------------------
    def _get(self, path: str, **params) -> dict:
        params["key"] = self.api_key
        resp = requests.get(f"{_API}/{path}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _uploads_playlist(self, channel_id: str) -> str:
        data = self._get("channels", part="contentDetails", id=channel_id)
        items = data.get("items", [])
        if not items:
            raise LookupError(f"channel not found: {channel_id}")
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _recent_video_ids(self, playlist_id: str, limit: int) -> List[str]:
        ids: List[str] = []
        page = None
        while len(ids) < limit:
            data = self._get(
                "playlistItems", part="contentDetails",
                playlistId=playlist_id, maxResults=min(50, limit - len(ids)),
                pageToken=page,
            )
            ids += [it["contentDetails"]["videoId"] for it in data.get("items", [])]
            page = data.get("nextPageToken")
            if not page:
                break
        return ids[:limit]

    def _videos(self, video_ids: List[str], creator: str) -> List[Video]:
        out: List[Video] = []
        for chunk_start in range(0, len(video_ids), 50):
            chunk = video_ids[chunk_start:chunk_start + 50]
            data = self._get(
                "videos", part="snippet,statistics", id=",".join(chunk),
            )
            for it in data.get("items", []):
                snip, stats = it["snippet"], it.get("statistics", {})
                vid = Video(
                    id=it["id"],
                    creator=creator,
                    platform="youtube",
                    title=snip["title"],
                    url=f"https://youtube.com/watch?v={it['id']}",
                    published_at=datetime.fromisoformat(
                        snip["publishedAt"].replace("Z", "+00:00")),
                    views=int(stats.get("viewCount", 0)),
                    likes=int(stats.get("likeCount", 0)),
                    comments=int(stats.get("commentCount", 0)),
                    hook=snip.get("description", "").split("\n")[0][:200],
                    thumbnail_url=snip.get("thumbnails", {})
                        .get("high", {}).get("url", ""),
                    tags=snip.get("tags", [])[:8],
                )
                out.append(vid)
        return out

    def top_videos(self, channel_id: str, creator: str, limit: int) -> List[Video]:
        playlist = self._uploads_playlist(channel_id)
        ids = self._recent_video_ids(playlist, limit * 2)  # over-fetch, rank later
        vids = self._videos(ids, creator)
        vids.sort(key=lambda v: v.views, reverse=True)
        return vids[:limit]

    def top_comments(self, video_id: str, limit: int = 8) -> List[str]:
        try:
            data = self._get(
                "commentThreads", part="snippet", videoId=video_id,
                order="relevance", maxResults=limit, textFormat="plainText",
            )
        except Exception:
            return []
        return [
            it["snippet"]["topLevelComment"]["snippet"]["textDisplay"][:240]
            for it in data.get("items", [])
        ]
