
from typing import List
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, func
from datetime import time as datetime_time

from api.database import Base

class ImageDto(BaseModel):
    image_url: str
    name: str
    created_at: datetime_time
    
    
class ImagesDto(BaseModel):
    images: List[ImageDto]
    
    
### Database Models ###

class ImageTable(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())