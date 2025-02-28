from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.enums.language_enums import LanguageEnum


class DeviceTokenTable(Base):
    """
    Table for storing device tokens for push notifications.
    """
    
    __tablename__ = "device_tokens"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    token = Column(Text, nullable=False, unique=True)
    device_type = Column(String(50), nullable=False)  # android, ios, web
    language = Column(String(10), nullable=True)  # Store language code (e.g., "de-DE", "en-US")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("UserTable", back_populates="device_tokens")
    
    def __repr__(self) -> str:
        return f"<DeviceToken(id={self.id}, user_id={self.user_id})>" 