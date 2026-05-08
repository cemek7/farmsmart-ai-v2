from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class IncomeCreate(BaseModel):
    crop_type: str
    amount: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    date: date
    expense_id: Optional[int] = None

    @field_validator("crop_type")
    @classmethod
    def normalise(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("crop_type must not be empty")
        return v.lower()


class IncomeUpdate(BaseModel):
    crop_type: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    quantity: Optional[float] = Field(None, gt=0)
    date: Optional[date] = None
    expense_id: Optional[int] = None

    @field_validator("crop_type")
    @classmethod
    def normalise(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("crop_type must not be empty")
        return v.lower()


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
