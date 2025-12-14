from pydantic import BaseModel

class VideoRequest(BaseModel):
    views: int
    likes: int
    comments: int
    shares: int
    saves: int
    engagement_rate: float
    trend_label: int
    platform: str  # "youtube" | "tiktok" | "both"


class CreatorRequest(BaseModel):
    channel_name: str
