import pandas as pd
import numpy as np
from backend.config import DATASET_PATH
import math
# =======================
# LOAD DATASET
# =======================
df = pd.read_csv(DATASET_PATH)
def encode_platform(video: dict) -> dict:
    video["platform_TikTok"] = 1 if video.get("platform") == "tiktok" else 0
    video["platform_YouTube"] = 1 if video.get("platform") == "youtube" else 0
    return video

# Encode trend_label (string -> numeric)
TREND_MAP = {
    "declining": 0,
    "stable": 1,
    "rising": 2
}

df["trend_label"] = df["trend_label"].map(TREND_MAP)

FEATURES = [
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "engagement_rate",
    "trend_label",
    "platform_TikTok",
    "platform_YouTube",
]

df_v = df[FEATURES].dropna().reset_index(drop=True)

# =======================
# MAIN FUNCTION (EXPORTED)
# =======================

def compute_virality_score(video):
    views = video["views"]
    engagement = video["engagement_rate"]
    trend = video.get("trend_label", 1)

    # 1️⃣ Volume (logarithmique)
    volume_score = min(math.log10(views + 1) / math.log10(50_000_000), 1)

    # 2️⃣ Engagement pondéré par fiabilité
    engagement_weight = min(views / 20_000, 1)
    engagement_score = min(engagement / 0.02, 2) / 2
    engagement_score *= engagement_weight

    # 3️⃣ Trend léger
    trend_score = 0.05 * trend

    raw = (
        0.6 * volume_score +
        0.35 * engagement_score +
        trend_score
    )

    # 4️⃣ Pénalité douce (PAS destructrice)
    if views < 10_000:
        penalty = 0.3 + 0.7 * (views / 10_000)
        raw *= penalty

    # 5️⃣ Clamp + plancher
    raw = max(raw, 0.01)   # jamais 0%
    raw = min(raw, 1.0)

    return round(raw * 100, 2)
