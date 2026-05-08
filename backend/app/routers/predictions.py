from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionRequest, PredictionRead

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("", response_model=PredictionRead, status_code=status.HTTP_201_CREATED)
async def make_prediction(
    payload: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.ml.predict import predict_revenue

    try:
        predicted_revenue, predicted_profit, model_used = predict_revenue(
            user_id=current_user.id,
            seed_cost=payload.seed_cost,
            fertilizer_cost=payload.fertilizer_cost,
            labor_cost=payload.labor_cost,
            irrigation_cost=payload.irrigation_cost,
            transport_cost=payload.transport_cost,
            farm_size=payload.farm_size,
            crop_type=payload.crop_type,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

    record = Prediction(
        user_id=current_user.id,
        crop_type=payload.crop_type,
        seed_cost=payload.seed_cost,
        fertilizer_cost=payload.fertilizer_cost,
        labor_cost=payload.labor_cost,
        irrigation_cost=payload.irrigation_cost,
        transport_cost=payload.transport_cost,
        farm_size=payload.farm_size,
        predicted_revenue=predicted_revenue,
        predicted_profit=predicted_profit,
        model_used=model_used,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/history", response_model=list[PredictionRead])
async def prediction_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prediction)
        .where(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .limit(10)
    )
    return result.scalars().all()
