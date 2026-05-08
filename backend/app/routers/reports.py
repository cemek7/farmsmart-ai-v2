from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.expense import Expense
from app.models.income import Income

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
async def get_report(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Build expense query
    expense_q = select(Expense).where(Expense.user_id == current_user.id)
    income_q = select(Income).where(Income.user_id == current_user.id)

    if year:
        expense_q = expense_q.where(extract("year", Expense.date) == year)
        income_q = income_q.where(extract("year", Income.date) == year)
    if month:
        expense_q = expense_q.where(extract("month", Expense.date) == month)
        income_q = income_q.where(extract("month", Income.date) == month)

    expenses = (await db.execute(expense_q)).scalars().all()
    incomes = (await db.execute(income_q)).scalars().all()

    total_expense = sum(e.total for e in expenses)
    total_income = sum(i.amount for i in incomes)
    net_profit = total_income - total_expense

    # Aggregate by crop
    expense_by_crop: dict[str, float] = {}
    for e in expenses:
        expense_by_crop[e.crop_type] = expense_by_crop.get(e.crop_type, 0.0) + e.total

    income_by_crop: dict[str, float] = {}
    for i in incomes:
        income_by_crop[i.crop_type] = income_by_crop.get(i.crop_type, 0.0) + i.amount

    return {
        "total_expense": total_expense,
        "total_income": total_income,
        "net_profit": net_profit,
        "expense_by_crop": expense_by_crop,
        "income_by_crop": income_by_crop,
    }
