from pydantic import BaseModel, RootModel
from typing import List
from api.database import Base
from sqlalchemy import Column, ForeignKeyConstraint, Integer, String, ForeignKey, Date
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



class MenuWeekTable(Base):
    __tablename__ = "menu_weeks"

    week = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)

    # Relationships
    canteen_id = Column(String, ForeignKey('canteens.canteen_id'))
    canteen = relationship("CanteenTable", back_populates="menu_weeks")
    menu_days = relationship("MenuDayTable", back_populates="menu_week", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MenuWeek(week='{self.week}', year='{self.year}')>"


class MenuDayTable(Base):
    __tablename__ = "menu_days"

    date = Column(Date, primary_key=True)
    menu_week_week = Column(Integer, nullable=False)
    menu_week_year = Column(Integer, nullable=False)
    
    # Define the foreign key constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ['menu_week_week', 'menu_week_year'],
            ['menu_weeks.week', 'menu_weeks.year']
        ),
    )

    # Relationships
    menu_week = relationship("MenuWeekTable", back_populates="menu_days")
    dishes = relationship("DishTable", back_populates="menu_day", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MenuDay(date='{self.date}', week='{self.menu_week_week}', year='{self.menu_week_year}')>"


