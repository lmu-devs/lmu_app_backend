import enum
from sqlalchemy import ARRAY, UUID, Column, Float, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.language_table import LanguageTable


class DishTable(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    dish_type = Column(String, nullable=False)
    dish_category = Column(String, nullable=False)
    labels = Column(ARRAY(String), nullable=False)
    price_simple = Column(String, nullable=True) # price abbreviation like 1 = €, 2 = €€, 3 = €€€ based on the price
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    menu_associations = relationship("MenuDishAssociation", back_populates="dish")
    prices = relationship("DishPriceTable", back_populates="dish", cascade="all, delete-orphan")
    likes = relationship("DishLikeTable", back_populates="dish", cascade="all, delete-orphan")
    translations = relationship("DishTranslationTable", back_populates="dish", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dish(id='{self.id}', type='{self.dish_type}')>"
    
    @property
    def like_count(self):
        return len(self.likes)

class PriceCategory(enum.Enum):
    STUDENT = "students"
    STAFF = "staff"
    GUEST = "guests"
 
class DishPriceTable(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    dish_id = Column(Integer, ForeignKey('dishes.id', ondelete='CASCADE'), nullable=False)
    base_price = Column(Float, nullable=True)
    price_per_unit = Column(Float, nullable=True)
    unit = Column(String, nullable=True)

    # Relationship
    dish = relationship("DishTable", back_populates="prices")

    def __repr__(self):
        return f"<Price(id='{self.id}', category='{self.category}', base_price='{self.base_price}', price_per_unit='{self.price_per_unit}', unit='{self.unit}')>"


# Table to represent the many-to-many relationship between dishes and users
class DishLikeTable(Base):
    __tablename__ = "dish_likes"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey('dishes.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    dish = relationship("DishTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_dishes")


    def __repr__(self):
        return f"<DishLike(dish_id='{self.dish_id}', user_id='{self.user_id}')>"

class DishTranslationTable(LanguageTable, Base):
    __tablename__ = "dish_translations"
    
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete='CASCADE'), nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    
    dish = relationship("DishTable", back_populates="translations")

