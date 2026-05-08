from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False)
    seed_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fertilizer_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    labor_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    irrigation_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    transport_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    other_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    farm_size: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="expenses")
    incomes: Mapped[list["Income"]] = relationship(
        "Income", back_populates="expense", foreign_keys="Income.expense_id"
    )

    @property
    def total(self) -> float:
        return (
            self.seed_cost
            + self.fertilizer_cost
            + self.labor_cost
            + self.irrigation_cost
            + self.transport_cost
            + self.other_cost
        )
