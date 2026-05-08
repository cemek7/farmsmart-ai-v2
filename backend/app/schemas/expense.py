from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    crop_type: str
    seed_cost: float = 0.0
    fertilizer_cost: float = 0.0
    labor_cost: float = 0.0
    irrigation_cost: float = 0.0
    transport_cost: float = 0.0
    other_cost: float = 0.0
    farm_size: float
    date: date


class ExpenseUpdate(BaseModel):
    crop_type: Optional[str] = None
    seed_cost: Optional[float] = None
    fertilizer_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    irrigation_cost: Optional[float] = None
    transport_cost: Optional[float] = None
    other_cost: Optional[float] = None
    farm_size: Optional[float] = None
    date: Optional[date] = None


class ExpenseRead(BaseModel):
    id: int
    user_id: int
    crop_type: str
    seed_cost: float
    fertilizer_cost: float
    labor_cost: float
    irrigation_cost: float
    transport_cost: float
    other_cost: float
    farm_size: float
    date: date
    created_at: datetime
    total: float

    model_config = {"from_attributes": True}
