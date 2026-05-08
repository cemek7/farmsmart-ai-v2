import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.income import Income
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeRead

router = APIRouter(prefix="/income", tags=["income"])


def _background_retrain(user_id: int) -> None:
    """Trigger retraining in a thread pool to avoid blocking the event loop."""
    from app.ml.train_models import maybe_retrain_user
    try:
        maybe_retrain_user(user_id)
    except Exception as exc:
        # Log but don't crash the request
        print(f"[ML] Retrain failed for user {user_id}: {exc}")


@router.get("", response_model=list[IncomeRead])
async def list_income(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Income)
        .where(Income.user_id == current_user.id)
        .order_by(Income.date.desc())
    )
    return result.scalars().all()


@router.post("", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
async def create_income(
    payload: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    income = Income(user_id=current_user.id, **payload.model_dump())
    db.add(income)
    await db.commit()
    await db.refresh(income)

    # Fire-and-forget retraining in thread pool
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _background_retrain, current_user.id)

    return income


@router.get("/{income_id}", response_model=IncomeRead)
async def get_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_owned_income(income_id, current_user.id, db)


@router.put("/{income_id}", response_model=IncomeRead)
async def update_income(
    income_id: int,
    payload: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    income = await _get_owned_income(income_id, current_user.id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(income, field, value)
    await db.commit()
    await db.refresh(income)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _background_retrain, current_user.id)

    return income


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    income = await _get_owned_income(income_id, current_user.id, db)
    await db.delete(income)
    await db.commit()


async def _get_owned_income(income_id: int, user_id: int, db: AsyncSession) -> Income:
    result = await db.execute(
        select(Income).where(Income.id == income_id, Income.user_id == user_id)
    )
    income = result.scalar_one_or_none()
    if income is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income record not found")
    return income
