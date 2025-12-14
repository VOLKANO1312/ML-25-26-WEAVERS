import pandas as pd
from backend.config import DATASET_PATH

# Chargement du dataset
df = pd.read_csv(DATASET_PATH)

# On utilise UNIQUEMENT la variable existante
COLUMN = "creator_avg_views"

# Sécurité : on enlève les NaN
df_creator = df[[COLUMN]].dropna()

# Définition des niveaux par quantiles (interprétable)
q1, q2, q3 = df_creator[COLUMN].quantile([0.25, 0.5, 0.75])

def predict_creator_level(avg_views: float, video_count: int) -> str:
    if avg_views > 1_000_000 and video_count > 200:
        return "Elite"
    elif avg_views > 200_000:
        return "Professional"
    elif avg_views > 50_000:
        return "Growing"
    else:
        return "Beginner"

