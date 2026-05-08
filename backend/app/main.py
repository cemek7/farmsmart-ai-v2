from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, expenses, income, reports, predictions

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables when using SQLite (local dev — Alembic handles production)
    if "sqlite" in settings.DATABASE_URL:
        from app.database import engine, Base
        import app.models  # noqa: F401 — ensures all models are registered
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Train baseline model on first startup if not already present
    import os
    from app.ml.train_models import MODELS_DIR
    baseline_path = os.path.join(MODELS_DIR, "baseline.joblib")
    if not os.path.exists(baseline_path):
        try:
            from app.ml.train_models import train_baseline
            print("[startup] Training baseline model from Nigerian crop data...")
            train_baseline()
        except Exception as exc:
            print(f"[startup] Baseline training failed: {exc}")
    yield


app = FastAPI(
    title="FarmSmart AI",
    version="2.0.0",
    description="Crop expense and revenue tracking with ML-powered predictions",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(income.router)
app.include_router(reports.router)
app.include_router(predictions.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
