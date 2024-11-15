from shared.database import Base
from sqlalchemy import Column, String, DateTime, UUID, func
from sqlalchemy.orm import relationship
import uuid

    
class UserTable(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    device_id = Column(String, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    api_key = Column(String, nullable=False) 
    creation_date = Column(DateTime, default=func.now())
    
    liked_dishes = relationship("DishLikeTable", back_populates="user")
    liked_canteens = relationship("CanteenLikeTable", back_populates="user")

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}')>"
