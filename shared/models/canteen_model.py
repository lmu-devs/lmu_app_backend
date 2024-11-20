from sqlalchemy import (UUID, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Time, func)
from sqlalchemy.orm import relationship

from shared.database import Base
from shared.models.image_model import ImageTable
from api.schemas.canteen_scheme import CanteenType


class CanteenTable(Base):
    __tablename__ = "canteens"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(CanteenType, name="canteen_type", create_type=False))

    location = relationship("LocationTable", uselist=False, back_populates="canteen", cascade="all, delete-orphan")
    opening_hours = relationship("OpeningHoursTable", back_populates="canteen", cascade="all, delete-orphan")
    menu_days = relationship("MenuDayTable", back_populates="canteen", cascade="all, delete-orphan")
    likes = relationship("CanteenLikeTable", back_populates="canteen", cascade="all, delete-orphan")
    images = relationship("CanteenImageTable", back_populates="canteen", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Canteen(id='{self.id}', name='{self.name}')>"
    
    @property
    def like_count(self):
        return len(self.likes)

class LocationTable(Base):
    __tablename__ = "locations"

    canteen_id = Column(String, ForeignKey('canteens.id'), primary_key=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    canteen = relationship("CanteenTable", back_populates="location")

class OpeningHoursTable(Base):
    __tablename__ = "opening_hours"

    canteen_id = Column(String, ForeignKey('canteens.id'), primary_key=True)
    day = Column(String, primary_key=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationships
    canteen = relationship("CanteenTable", back_populates="opening_hours")
    
    
# Table to represent the many-to-many relationship between dishes and users
class CanteenLikeTable(Base):
    __tablename__ = "canteen_likes"

    id = Column(Integer, primary_key=True, index=True)
    canteen_id = Column(String, ForeignKey('canteens.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True),  ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    canteen = relationship("CanteenTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_canteens")

    def __repr__(self):
        return f"<CanteenLike(canteen_id='{self.canteen_id}', user_id='{self.user_id}')>"
    
    
# Table to represent the many-to-many relationship between canteens and images
class CanteenImageTable(ImageTable, Base):
    __tablename__ = "canteen_images"

    canteen_id = Column(String, ForeignKey('canteens.id'), nullable=False)

    canteen = relationship("CanteenTable", back_populates="images")
    
    def __repr__(self):
        return f"<CanteenImage(canteen_id='{self.canteen_id}')>"


