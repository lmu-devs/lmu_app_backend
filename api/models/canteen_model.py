import enum
from pydantic import BaseModel, ConfigDict, RootModel
from typing import List, Optional
from api.database import Base
from sqlalchemy import UUID, Column, DateTime, Integer, String, ForeignKey, Time, Float, Enum, func
from sqlalchemy.orm import relationship
from datetime import time as datetime_time

from api.models.image_model import ImageDto
from api.models.rating_model import RatingDto

class Weekday(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    
class CanteenType(str, enum.Enum):
    MENSA = "MENSA"
    STUBISTRO = "STUBISTRO"
    STUCAFE = "STUCAFE"
    


class LocationDto(BaseModel):
    address: str
    latitude: float
    longitude: float
    
class OpeningHoursDto(BaseModel):
    day: Weekday
    start_time: Optional[datetime_time]
    end_time: Optional[datetime_time]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    
class CanteenDto(BaseModel):
    id: str
    name: str
    type: CanteenType
    location: LocationDto
    rating: RatingDto
    opening_hours: List[OpeningHoursDto]
    images: List[ImageDto]
    
class CanteensDto(RootModel):
    root: List[CanteenDto]




### Database Models ###


class CanteenTable(Base):
    __tablename__ = "canteens"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(CanteenType, name="canteen_type", create_type=False))

    # Relationships
    location = relationship("LocationTable", uselist=False, back_populates="canteen", cascade="all, delete-orphan")
    opening_hours = relationship("OpeningHoursTable", back_populates="canteen", cascade="all, delete-orphan")
    menu_weeks = relationship("MenuWeekTable", back_populates="canteen", cascade="all, delete-orphan")
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

    canteen = relationship("CanteenTable", back_populates="opening_hours")
    
    
# Table to represent the many-to-many relationship between dishes and users
class CanteenLikeTable(Base):
    __tablename__ = "canteen_likes"

    id = Column(Integer, primary_key=True, index=True)
    canteen_id = Column(String, ForeignKey('canteens.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True),  ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    canteen = relationship("CanteenTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_canteens")

    def __repr__(self):
        return f"<CanteenLike(canteen_id='{self.canteen_id}', user_id='{self.user_id}')>"
    
    
# Table to represent the many-to-many relationship between canteens and images
class CanteenImageTable(Base):
    __tablename__ = "canteen_images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    canteen_id = Column(String, ForeignKey('canteens.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    canteen = relationship("CanteenTable", back_populates="images")
    
    def __repr__(self):
        return f"<CanteenImage(canteen_id='{self.canteen_id}')>"


