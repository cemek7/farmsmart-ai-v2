from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    crop_type: str
    seed_cost: float = Field(0.0, ge=0)
    fertilizer_cost: float = Field(0.0, ge=0)
    labor_cost: float = Field(0.0, ge=0)
    irrigation_cost: float = Field(0.0, ge=0)
    transport_cost: float = Field(0.0, ge=0)
    other_cost: float = Field(0.0, ge=0)
    farm_size: float = Field(..., gt=0)
    date: date

    @field_validator("crop_type")
    @classmethod
    def normalise(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("crop_type must not be empty")
        return v.lower()


class ExpenseUpdate(BaseModel):
    crop_type: Optional[str] = None
    seed_cost: Optional[float] = Field(None, ge=0)
    fertilizer_cost: Optional[float] = Field(None, ge=0)
    labor_cost: Optional[float] = Field(None, ge=0)
    irrigation_cost: Optional[float] = Field(None, ge=0)
    transport_cost: Optional[float] = Field(None, ge=0)
    other_cost: Optional[float] = Field(None, ge=0)
    farm_size: Optional[float] = Field(None, gt=0)
    date: Optional[date] = None

    @field_validator("crop_type")
    @classmethod
    def normalise(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("crop_type must not be empty")
        return v.lower()


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
