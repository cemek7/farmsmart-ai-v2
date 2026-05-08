"""
ML training module — uses sync SQLAlchemy session since training runs
as a background task, not in the async request path.
"""
import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
FEATURE_COLS = [
    "seed_cost", "fertilizer_cost", "labor_cost",
    "irrigation_cost", "transport_cost", "farm_size", "crop_type_encoded"
]
CROP_ENCODER = {"maize": 0, "rice": 1, "cassava": 2, "yam": 3, "tomato": 4}
MIN_PAIRS = 5


def _get_pairs(user_id=None) -> list[dict]:
    """Pull paired (expense, income) records using a sync DB session."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.config import get_settings
    from app.models.income import Income
    from app.models.expense import Expense

    settings = get_settings()
    # Convert async driver URL to sync equivalent for background training
    sync_url = settings.DATABASE_URL
    if "+asyncpg://" in sync_url:
        sync_url = sync_url.replace("+asyncpg://", "+psycopg2://")
    elif "+aiosqlite" in sync_url:
        sync_url = sync_url.replace("+aiosqlite", "")

    try:
        engine = create_engine(sync_url)
        with Session(engine) as session:
            stmt = select(Income).where(Income.expense_id.isnot(None))
            if user_id is not None:
                stmt = stmt.where(Income.user_id == user_id)

            rows = []
            for inc in session.scalars(stmt).all():
                exp = session.get(Expense, inc.expense_id)
                if exp is None:
                    continue
                rows.append({
                    "seed_cost": exp.seed_cost,
                    "fertilizer_cost": exp.fertilizer_cost,
                    "labor_cost": exp.labor_cost,
                    "irrigation_cost": exp.irrigation_cost,
                    "transport_cost": exp.transport_cost,
                    "farm_size": exp.farm_size,
                    "crop_type_encoded": CROP_ENCODER.get(exp.crop_type.lower(), 0),
                    "revenue": inc.amount,
                })
            return rows
    except Exception:
        # If DB not reachable (e.g. tests), return empty
        return []


def _train_and_save(rows: list[dict], model_path: str) -> None:
    X = np.array([[r[c] for c in FEATURE_COLS] for r in rows])
    y = np.array([r["revenue"] for r in rows])

    if len(rows) >= 10:
        X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_tr, y_tr = X, y

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_tr, y_tr)
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, model_path)

    # Evict cached entry so next prediction loads the fresh model
    from app.ml.predict import _cache
    _cache.pop(model_path, None)


def maybe_retrain_user(user_id: int) -> None:
    """Called after each income record save. Retrains personal + community models if enough data."""
    rows = _get_pairs(user_id=user_id)
    if len(rows) >= MIN_PAIRS:
        _train_and_save(rows, os.path.join(MODELS_DIR, f"user_{user_id}.joblib"))

    all_rows = _get_pairs(user_id=None)
    if len(all_rows) >= MIN_PAIRS:
        _train_and_save(all_rows, os.path.join(MODELS_DIR, "community.joblib"))


def train_baseline() -> None:
    """Train the baseline model from Nigerian crop data. Run once on first deploy."""
    from app.ml.baseline_data import load, COLUMNS

    df = load()
    rows = df.to_dict("records")
    _train_and_save(rows, os.path.join(MODELS_DIR, "baseline.joblib"))
    print(f"Baseline model trained and saved to {MODELS_DIR}/baseline.joblib")
