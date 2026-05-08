from datetime import datetime
from pydantic import BaseModel


class PredictionRequest(BaseModel):
    crop_type: str
    seed_cost: float
    fertilizer_cost: float
    labor_cost: float
    irrigation_cost: float
    transport_cost: float
    farm_size: float


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
