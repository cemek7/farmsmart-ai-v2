from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    crop_type: str
    seed_cost: float = Field(0.0, ge=0)
    fertilizer_cost: float = Field(0.0, ge=0)
    labor_cost: float = Field(0.0, ge=0)
    irrigation_cost: float = Field(0.0, ge=0)
    transport_cost: float = Field(0.0, ge=0)
    farm_size: float = Field(..., gt=0)

    @field_validator("crop_type")
    @classmethod
    def normalise(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("crop_type must not be empty")
        return v.lower()


class PredictionRead(BaseModel):
    id: int
    user_id: int
    crop_type: str
    seed_cost: float
    fertilizer_cost: float
    labor_cost: float
    irrigation_cost: float
    transport_cost: float
    farm_size: float
    predicted_revenue: float
    predicted_profit: float
    model_used: str
    created_at: datetime

    model_config = {"from_attributes": True}
