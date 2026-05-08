from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class IncomeCreate(BaseModel):
    crop_type: str
    amount: float
    quantity: float
    date: date
    expense_id: Optional[int] = None


class IncomeUpdate(BaseModel):
    crop_type: Optional[str] = None
    amount: Optional[float] = None
    quantity: Optional[float] = None
    date: Optional[date] = None
    expense_id: Optional[int] = None


class IncomeRead(BaseModel):
    id: int
    user_id: int
    crop_type: str
    amount: float
    quantity: float
    date: date
    expense_id: Optional[int]
    created_at: datetime
    is_paired: bool

    model_config = {"from_attributes": True}
