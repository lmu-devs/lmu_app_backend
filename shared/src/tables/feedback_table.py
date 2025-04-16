from datetime import datetime
from enum import Enum

from sqlalchemy import ARRAY, UUID, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


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
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    type = Column(String, nullable=False)
    rating = Column(String, nullable=True)
    message = Column(String, nullable=True)
    screen = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    app_version = Column(String, nullable=True)
    system_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship with user
    user = relationship("UserTable", back_populates="feedback")
