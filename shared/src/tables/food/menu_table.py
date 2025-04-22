from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class MenuDishAssociation(Base):
    __tablename__ = "menu_dish_associations"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(UUID(as_uuid=True), ForeignKey("dishes.id"), nullable=False)
    menu_day_date = Column(Date, nullable=False)
    canteen_id = Column(String, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(["menu_day_date", "canteen_id"], ["menu_days.date", "menu_days.canteen_id"]),
    )

    dish = relationship("DishTable", back_populates="menu_associations")
    menu_day = relationship("MenuDayTable", back_populates="dish_associations")

    def __repr__(self):
        return f"<MenuDishAssociation(dish_id='{self.dish_id}', date='{self.menu_day_date}', canteen_id='{self.canteen_id}')>"


class MenuDayTable(Base):
    __tablename__ = "menu_days"

    date = Column(Date, primary_key=True)
    canteen_id = Column(String, ForeignKey("canteens.id", ondelete="CASCADE"), primary_key=True)
    is_closed = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    canteen = relationship("CanteenTable", back_populates="menu_days")
    dish_associations = relationship("MenuDishAssociation", back_populates="menu_day", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MenuDay(date='{self.date}', canteen_id='{self.canteen_id}')>"
