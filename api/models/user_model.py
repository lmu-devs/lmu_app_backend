from pydantic import BaseModel
from typing import List
from api.database import Base
from sqlalchemy import Column, String, Date, UUID
from sqlalchemy.orm import relationship
from datetime import date
import uuid

class UserDto(BaseModel):
    id: uuid.UUID
    device_id: str
    name: str
    email: str
    password: str
    creation_date: date
    

# Tables
    
class UserTable(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    device_id = Column(String, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    creation_date = Column(Date, nullable=True)
    
    liked_dishes = relationship("DishLikeTable", back_populates="user")

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}')>"
