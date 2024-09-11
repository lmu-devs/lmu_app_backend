from pydantic import BaseModel, RootModel
from typing import List
from api.database import Base
from sqlalchemy import Column, ForeignKeyConstraint, Integer, String, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import date

from api.models.dish_model import DishDto



    
class MenuDayDto(BaseModel):
    date: date
    dishes: List[DishDto]
    
class MenuWeekDto(BaseModel):
    week: int
    year: int
    canteen_id: str
    menu_days: List[MenuDayDto]
    
class MenusDto(RootModel):
    root: List[MenuWeekDto]
    


### Database Models ###

class MenuDishAssociation(Base):
    __tablename__ = "menu_dish_associations"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey('dishes.id'), nullable=False)
    menu_day_date = Column(Date, nullable=False)
    menu_day_canteen_id = Column(String, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['menu_day_date', 'menu_day_canteen_id'],
            ['menu_days.date', 'menu_days.menu_week_canteen_id']
        ),
    )

    # Relationships
    dish = relationship("DishTable", back_populates="menu_associations")
    menu_day = relationship("MenuDayTable", back_populates="dish_associations")

    def __repr__(self):
        return f"<MenuDishAssociation(dish_id='{self.dish_id}', date='{self.menu_day_date}', canteen_id='{self.menu_day_canteen_id}')>"



class MenuWeekTable(Base):
    __tablename__ = "menu_weeks"

    week = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    canteen_id = Column(String, ForeignKey('canteens.canteen_id'), primary_key=True)

    # Relationships
    canteen = relationship("CanteenTable", back_populates="menu_weeks")
    menu_days = relationship("MenuDayTable", back_populates="menu_week", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MenuWeek(week='{self.week}', year='{self.year}', canteen_id='{self.canteen_id}')>"


class MenuDayTable(Base):
    __tablename__ = "menu_days"

    date = Column(Date, primary_key=True)
    menu_week_canteen_id = Column(String, nullable=False, primary_key=True)
    menu_week_week = Column(Integer, nullable=False)
    menu_week_year = Column(Integer, nullable=False)
    
    
    # Define the foreign key constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ['menu_week_week', 'menu_week_year', 'menu_week_canteen_id'],
            ['menu_weeks.week', 'menu_weeks.year', 'menu_weeks.canteen_id']
        ),
        # UniqueConstraint('date', 'menu_week_canteen_id', name='uq_menu_day_date_canteen'),
    )

    # Relationships
    menu_week = relationship("MenuWeekTable", back_populates="menu_days")
    dish_associations = relationship("MenuDishAssociation", back_populates="menu_day", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MenuDay(date='{self.date}', week='{self.menu_week_week}', year='{self.menu_week_year}', canteen_id='{self.menu_week_canteen_id}')>"


