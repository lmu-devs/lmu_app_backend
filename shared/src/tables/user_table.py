import uuid

from sqlalchemy import UUID, Column, DateTime, String, func
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class UserTable(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    api_key = Column(String, nullable=False)
    device_id = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    liked_dishes = relationship("DishLikeTable", back_populates="user", cascade="all, delete-orphan")
    liked_canteens = relationship("CanteenLikeTable", back_populates="user", cascade="all, delete-orphan")
    liked_wishlists = relationship("WishlistLikeTable", back_populates="user", cascade="all, delete-orphan")
    liked_libraries = relationship("LibraryLikeTable", back_populates="user", cascade="all, delete-orphan")
    liked_screenings = relationship("ScreeningLikeTable", back_populates="user", cascade="all, delete-orphan")
    liked_link_resources = relationship("LinkResourceLikeTable", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("FeedbackTable", back_populates="user")

    def __repr__(self):
        return f"<User(id='{self.id}')>"
