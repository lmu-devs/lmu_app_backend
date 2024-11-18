from enum import Enum
from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from shared.database import Base
from datetime import datetime

class FeedbackRating(str, Enum):
    BAD = "BAD"
    NEUTRAL = "NEUTRAL"
    GOOD = "GOOD"
    
class FeedbackType(str, Enum):
    BUG = "BUG"
    SUGGESTION = "SUGGESTION"
    GENERAL = "GENERAL"

class FeedbackTable(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)
    rating = Column(String, nullable=False)
    message = Column(String, nullable=True)
    screen = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship with user
    user = relationship("UserTable", back_populates="feedback") 