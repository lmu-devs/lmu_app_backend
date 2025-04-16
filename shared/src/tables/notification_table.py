import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.language_table import LanguageTable


class NotificationTable(Base):
    """
    Table for storing notifications.
    """

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_url = Column(String(255), nullable=True)
    data = Column(JSONB, nullable=True)
    topic = Column(String(100), nullable=True)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    translations = relationship(
        "NotificationTranslationTable",
        back_populates="notification",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id})>"


class NotificationTranslationTable(LanguageTable):
    __tablename__ = "notification_translations"

    notification_id = Column(
        UUID, ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True
    )
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    notification = relationship("NotificationTable", back_populates="translations")
