from pydantic import BaseModel
from typing import List
from api.database import Base
from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class UserDto(BaseModel):
    id: uuid.UUID
    device_id: str
    name: str | None
    email: str | None
    password: str | None
    api_key: str
    creation_date: datetime
    

# Tables
    
class UserTable(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    device_id = Column(String, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    api_key = Column(String, nullable=False) 
    creation_date = Column(DateTime, nullable=False)
    
    liked_dishes = relationship("DishLikeTable", back_populates="user")

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}')>"
