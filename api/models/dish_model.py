import enum
from typing import List
from pydantic import BaseModel, RootModel
from sqlalchemy import ARRAY, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from datetime import date


from api.database import Base
from api.models.canteen_model import CanteenDto


class DishPriceDto(BaseModel):
    category: str
    base_price: float
    price_per_unit: float
    unit: str
    
class DishDto(BaseModel):
    name: str
    dish_type: str
    labels: List[str]
    prices: List[DishPriceDto]
    
    

class DishDateDto(BaseModel):
    date: date
    canteens: List[CanteenDto]

class DishDatesDto(BaseModel):
    dates: List[DishDateDto]
    
    
    
    
    
### Database Models ###

class DishTable(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dish_type = Column(String, nullable=False)
    labels = Column(ARRAY(String), nullable=False)

    # Foreign key
    menu_day_date = Column(Date, ForeignKey('menu_days.date'))

    # Relationship
    menu_day = relationship("MenuDayTable", back_populates="dishes")
    prices = relationship("DishPriceTable", back_populates="dish", cascade="all, delete-orphan")
    # users - liked by?

    def __repr__(self):
        return f"<Dish(id='{self.id}', name='{self.name}', type='{self.dish_type}')>"
    

class PriceCategory(enum.Enum):
    STUDENT = "students"
    STAFF = "staff"
    GUEST = "guests"
 
class DishPriceTable(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    dish_id = Column(Integer, ForeignKey('dishes.id'), nullable=False)
    base_price = Column(Float, nullable=True)
    price_per_unit = Column(Float, nullable=True)
    unit = Column(String, nullable=True)

    # Relationship
    dish = relationship("DishTable", back_populates="prices")

    def __repr__(self):
        return f"<Price(id='{self.id}', category='{self.category}', base_price='{self.base_price}', price_per_unit='{self.price_per_unit}', unit='{self.unit}')>"

