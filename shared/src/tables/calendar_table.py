from sqlalchemy import Column, DateTime, String, ForeignKey, Integer, Boolean
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.src.core.database import Base
from enum import Enum

class EventType(str, Enum): # not complete
    MOVIE = "MOVIE",
    SPORT = "SPORT",
    LECTURE = "LECTURE",

class RepeatType(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class CalendarTable(Base):
    __tablename__ = "calendar"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True) # maybe set a char limit
    #location = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, default=False, nullable=False)

    repeat_type = Column(String, nullable=False)
    repeat_interval = Column(Integer, nullable=False)
    repeat_end_time = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("UserTable", back_populates="calendar")

