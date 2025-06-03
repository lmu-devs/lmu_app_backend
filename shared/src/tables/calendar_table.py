from sqlalchemy import Column, DateTime, String, ForeignKey
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.src.core.database import Base
from enum import Enum

class EventType(str, Enum): # not complete, translation?
    MOVIE = "MOVIE",
    SPORT = "SPORT",

class RepeatType(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class CalendarTable(Base):
    __tablename__ = "calendar"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True) # maybe set a char limit
    #location = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    repeat_type = Column(String, nullable=False) # Implement daily, weekly, etc -> set max limit for one event
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("UserTable", back_populates="calendar")

