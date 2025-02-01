from sqlalchemy import UUID, Column, DateTime, ForeignKey, func
from sqlalchemy.orm import declared_attr, relationship

from shared.src.core.database import Base


class LikeTable:
    """
    Abstract base class for like tables that implements common like functionality
    """
    
    @declared_attr
    def user_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    
    @declared_attr
    def user(cls):
        return relationship("UserTable", back_populates=f"{cls.__tablename__}")
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now())
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<{self.__class__.__name__}({', '.join(f'{key}={value!r}' for key, value in self.__dict__.items() if not key.startswith('_'))})>"
