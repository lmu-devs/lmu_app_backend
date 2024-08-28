from pydantic import BaseModel, ConfigDict, RootModel
from typing import List, Optional
import enum
from api.database import Base
from sqlalchemy import Column, String, ForeignKey, Time, Float
from sqlalchemy.orm import relationship
from datetime import time as datetime_time

class Weekday(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

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
    canteen_id: str
    name: str
    location: LocationDto
    opening_hours: List[OpeningHoursDto]
    
class CanteensDto(RootModel):
    root: List[CanteenDto]




### Database Models ###


class CanteenTable(Base):
    __tablename__ = "canteens"

    canteen_id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    location = relationship("LocationTable", uselist=False, back_populates="canteen", cascade="all, delete-orphan")
    opening_hours = relationship("OpeningHoursTable", back_populates="canteen", cascade="all, delete-orphan")
    menu_weeks = relationship("MenuWeekTable", back_populates="canteen", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Canteen(canteen_id='{self.canteen_id}', name='{self.name}')>"

class LocationTable(Base):
    __tablename__ = "locations"

    canteen_id = Column(String, ForeignKey('canteens.canteen_id'), primary_key=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    canteen = relationship("CanteenTable", back_populates="location")

class OpeningHoursTable(Base):
    __tablename__ = "opening_hours"

    canteen_id = Column(String, ForeignKey('canteens.canteen_id'), primary_key=True)
    day = Column(String, primary_key=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    canteen = relationship("CanteenTable", back_populates="opening_hours")


