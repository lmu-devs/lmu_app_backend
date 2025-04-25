from typing import List

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship

from shared.src.db.base_class import Base
from shared.src.models.opening_hours.base import BaseOpeningHours, BaseTimeRangeModel


class CanteenTimeRange(BaseTimeRangeModel):
    __tablename__ = "canteen_time_ranges"

    opening_hours_id = Column(Integer, ForeignKey("canteen_opening_hours.id"))
    opening_hours = relationship("CanteenOpeningHours", back_populates="time_ranges")


class CanteenOpeningHours(Base, BaseOpeningHours):
    __tablename__ = "canteen_opening_hours"

    canteen_id = Column(Integer, ForeignKey("canteens.id"), nullable=False)

    # Relationships
    canteen = relationship("Canteen", back_populates="opening_hours")
    time_ranges: Mapped[List[CanteenTimeRange]] = relationship(
        "CanteenTimeRange", back_populates="opening_hours", cascade="all, delete-orphan"
    )

    @property
    def time_range_class(self):
        return CanteenTimeRange
