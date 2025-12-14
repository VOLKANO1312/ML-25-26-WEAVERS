import os
import requests
import pandas as pd
from urllib.parse import urlparse, parse_qs
from backend.config import DATASET_PATH

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
print("YOUTUBE_API_KEY =", YOUTUBE_API_KEY)

# ==================================================
# UTIL
# ==================================================
def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    if "youtube.com" in parsed.netloc:
        return parse_qs(parsed.query).get("v", [None])[0]

    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    return None


# ==================================================
# VIDEO STATS (YOUTUBE API)
# ==================================================
def fetch_video_stats(video_url: str) -> dict:
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube video URL")

    api_url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
    )

    r = requests.get(api_url).json()

    # DEBUG
    print("YOUTUBE VIDEO API RESPONSE:", r)

    if "error" in r:
        raise ValueError(r["error"]["message"])

    if "items" not in r or len(r["items"]) == 0:
        raise ValueError("Video not found (private / deleted / invalid)")

    stats = r["items"][0]["statistics"]

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))

    engagement_rate = (likes + comments) / views if views > 0 else 0

    return {
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": 0,
        "saves": 0,
        "engagement_rate": engagement_rate,
        "trend_label": 1,
        "platform": "youtube"  # ⚠️ cohérent avec le modèle
    }


# ==================================================
# CREATOR STATS (DATASET OFFLINE)
# ==================================================
def get_creator_stats(channel_name: str) -> dict:
    """
    Stats créateur basées sur le DATASET (stable, académique)
    """
    df = pd.read_csv(DATASET_PATH)

    if "creator" in df.columns:
        row = df[df["creator"].str.lower() == channel_name.lower()]
        if not row.empty:
            stats = {
                "creator_avg_views": float(row.iloc[0]["creator_avg_views"]),
                "creator_avg_likes": float(row.iloc[0].get("creator_avg_likes", 0)),
                "creator_avg_comments": float(row.iloc[0].get("creator_avg_comments", 0)),
                "creator_avg_engagement_rate": float(row.iloc[0].get("creator_avg_engagement_rate", 0)),
                "creator_video_count": int(row.iloc[0].get("creator_video_count", 1)),
            }

            print("DATASET CREATOR STATS:", stats)
            return stats

    # fallback
    stats = {
        "creator_avg_views": float(df["creator_avg_views"].median()),
        "creator_video_count": int(df.get("creator_video_count", pd.Series([1])).median())
    }

    print("DATASET CREATOR FALLBACK:", stats)
    return stats
def fetch_channel_stats(channel_url: str) -> dict:
    """
    Extract channel statistics from YouTube API
    """
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY is not set")

    # ⚠️ Cas 1 : URL directe de chaîne
    if "youtube.com" in channel_url and "/@" in channel_url:
        channel_name = channel_url.split("/@")[-1]
        search_url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&type=channel&q={channel_name}&key={YOUTUBE_API_KEY}"
        )
        search = requests.get(search_url).json()

        if "items" not in search or not search["items"]:
            raise ValueError("Channel not found")

        channel_id = search["items"][0]["snippet"]["channelId"]
    else:
        # fallback simple
        channel_id = channel_url

    stats_url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
    )

    r = requests.get(stats_url).json()
    print("YouTube CHANNEL API response:", r)

    if "items" not in r or not r["items"]:
        raise ValueError("No channel statistics found")

    stats = r["items"][0]["statistics"]

    views = int(stats.get("viewCount", 0))
    videos = int(stats.get("videoCount", 1))
    subscribers = int(stats.get("subscriberCount", 0))

    return {
        "creator_avg_views": views / max(videos, 1),
        "creator_video_count": videos,
        "creator_subscribers": subscribers
    }
