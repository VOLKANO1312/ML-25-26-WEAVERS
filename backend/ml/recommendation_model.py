import pandas as pd
import numpy as np
from backend.config import DATASET_PATH
import math

df = pd.read_csv(DATASET_PATH)
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

df_r = df[FEATURES].dropna().reset_index(drop=True)
df["trend_score"] = df["views"] * df["engagement_rate"]
threshold = df["trend_score"].median()

import math

def compute_recommendation_probability(video: dict) -> float:
    views = video["views"]
    engagement = video["engagement_rate"]

    # 1️⃣ Score engagement normalisé
    engagement_score = min(engagement / 0.08, 1.0)  # 8% = très fort

    # 2️⃣ Score volume (logarithmique)
    volume_score = min(math.log10(views + 1) / 8, 1.0)
    # log10(100M) ≈ 8 → score max

    # 3️⃣ Pondération dynamique
    if views > 5_000_000:
        final_score = 0.35 * engagement_score + 0.65 * volume_score
    else:
        final_score = 0.65 * engagement_score + 0.35 * volume_score

    return round(min(final_score, 0.99), 3)

