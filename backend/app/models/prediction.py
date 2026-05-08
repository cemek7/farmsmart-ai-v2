from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    seed_cost: Mapped[float] = mapped_column(Float, nullable=False)
    fertilizer_cost: Mapped[float] = mapped_column(Float, nullable=False)
    labor_cost: Mapped[float] = mapped_column(Float, nullable=False)
    irrigation_cost: Mapped[float] = mapped_column(Float, nullable=False)
    transport_cost: Mapped[float] = mapped_column(Float, nullable=False)
    farm_size: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_profit: Mapped[float] = mapped_column(Float, nullable=False)
    model_used: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="predictions")
