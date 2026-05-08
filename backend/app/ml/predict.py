import os
import joblib
import numpy as np
from app.ml.train_models import CROP_ENCODER, FEATURE_COLS

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
_cache: dict = {}


def _load(path: str):
    if path not in _cache:
        _cache[path] = joblib.load(path)
    return _cache[path]


def get_model_for_user(user_id: int) -> tuple:
    """Returns (model, tier_label). Tries personal → community → baseline."""
    personal = os.path.join(MODELS_DIR, f"user_{user_id}.joblib")
    community = os.path.join(MODELS_DIR, "community.joblib")
    baseline = os.path.join(MODELS_DIR, "baseline.joblib")

    if os.path.exists(personal):
        return _load(personal), "personal"
    if os.path.exists(community):
        return _load(community), "community"
    if os.path.exists(baseline):
        return _load(baseline), "baseline"
    return None, None


def predict_revenue(
    user_id: int,
    seed_cost: float,
    fertilizer_cost: float,
    labor_cost: float,
    irrigation_cost: float,
    transport_cost: float,
    farm_size: float,
    crop_type: str,
) -> tuple[float, float, str]:
    """Returns (predicted_revenue, predicted_profit, model_used)."""
    model, tier = get_model_for_user(user_id)
    if model is None:
        raise RuntimeError(
            "No model available. Run: python -c \"from app.ml.train_models import train_baseline; train_baseline()\""
        )

    crop_lower = crop_type.lower()
    if crop_lower not in CROP_ENCODER:
        raise ValueError(f"Unknown crop type: {crop_type!r}. Supported: {list(CROP_ENCODER)}")

    crop_encoded = CROP_ENCODER[crop_lower]
    X = np.array([[seed_cost, fertilizer_cost, labor_cost,
                   irrigation_cost, transport_cost, farm_size, crop_encoded]])
    revenue = float(model.predict(X)[0])
    total_cost = seed_cost + fertilizer_cost + labor_cost + irrigation_cost + transport_cost
    profit = revenue - total_cost
    return revenue, profit, tier
