from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.schemas import VideoRequest
from backend.ml.virality_model import compute_virality_score
from backend.ml.recommendation_model import compute_recommendation_probability
from backend.ml.creator_level_model import predict_creator_level

from backend.services.youtube_client import (
    fetch_video_stats,
    fetch_channel_stats,
    get_creator_stats
)

app = FastAPI(title="Weavers Video Intelligence")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# FRONTEND
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================================================
# 🎥 VIDEO – MANUAL (OPTIONAL)
# =========================================================
@app.post("/analyze/video/manual")
def analyze_video_manual(video: VideoRequest):
    data = video.dict()
    return {
        "source": "manual",
        "virality_score": compute_virality_score(data),
        "recommendation_probability": compute_recommendation_probability(data),
        "input_used": data
    }

# =========================================================
# 🎥 VIDEO – YOUTUBE (PRIORITY)
# =========================================================
@app.post("/analyze/video/youtube")
def analyze_video_youtube(payload: dict):
    if "url" not in payload:
        raise HTTPException(400, "Missing YouTube video URL")

    try:
        video = fetch_video_stats(payload["url"])
    except Exception as e:
        raise HTTPException(400, str(e))

    return {
        "source": "youtube_api",
        "virality_score": compute_virality_score(video),
        "recommendation_probability": compute_recommendation_probability(video),
        "video_stats": video
    }

# =========================================================
# 👤 CREATOR – YOUTUBE (API)
# =========================================================
@app.post("/analyze/creator/youtube")
def analyze_creator_youtube(payload: dict):
    if "url" not in payload:
        raise HTTPException(400, "Missing channel URL")

    try:
        stats = fetch_channel_stats(payload["url"])
    except Exception as e:
        raise HTTPException(400, str(e))

    level = predict_creator_level(
        avg_views=stats["creator_avg_views"],
        video_count=stats["creator_video_count"]
    )

    return {
        "source": "youtube_api",
        "creator_level": level,
        "stats_used": stats
    }

# =========================================================
# 👤 CREATOR – DATASET (FALLBACK)
# =========================================================
@app.post("/analyze/creator/dataset")
def analyze_creator_dataset(payload: dict):
    if "channel_name" not in payload:
        raise HTTPException(400, "Missing channel_name")

    stats = get_creator_stats(payload["channel_name"])

    level = predict_creator_level(
        avg_views=stats["creator_avg_views"],
        video_count=stats.get("creator_video_count", 1)
    )

    return {
        "source": "dataset",
        "creator_level": level,
        "stats_used": stats
    }
