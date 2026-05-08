import asyncio
from typing import Optional
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
    """Run in executor — sync, catches all exceptions so it never crashes the request."""
    from app.ml.train_models import maybe_retrain_user
    try:
        maybe_retrain_user(user_id)
    except Exception as exc:
        print(f"[ML] Retrain failed for user {user_id}: {exc}")


async def _validate_expense_id(expense_id: Optional[int], user_id: int, db: AsyncSession) -> Optional[int]:
    """Silently drops expense_id that doesn't belong to the current user."""
    if expense_id is None:
        return None
    from app.models.expense import Expense
    exp = await db.get(Expense, expense_id)
    if exp is None or exp.user_id != user_id:
        return None
    return expense_id


@router.get("", response_model=list[IncomeRead])
async def list_income(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id).order_by(Income.date.desc())
    )
    return result.scalars().all()


@router.post("", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
async def create_income(
    payload: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = payload.model_dump()
    data["expense_id"] = await _validate_expense_id(data.get("expense_id"), current_user.id, db)
    income = Income(user_id=current_user.id, **data)
    db.add(income)
    await db.commit()
    await db.refresh(income)
    asyncio.get_running_loop().run_in_executor(None, _background_retrain, current_user.id)
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
    update_data = payload.model_dump(exclude_unset=True)
    if "expense_id" in update_data:
        update_data["expense_id"] = await _validate_expense_id(update_data["expense_id"], current_user.id, db)
    for field, value in update_data.items():
        setattr(income, field, value)
    await db.commit()
    await db.refresh(income)
    asyncio.get_running_loop().run_in_executor(None, _background_retrain, current_user.id)
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
