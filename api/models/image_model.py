
from typing import List
from pydantic import BaseModel


from api.database import Base

class ImageDto(BaseModel):
    url: str
    name: str
    # created_at: datetime_time

    
    
### Database Models ###

# class ImageTable(Base):
#     __tablename__ = "images"

#     id = Column(Integer, primary_key=True, index=True)
#     image_url = Column(String, nullable=False)
#     name = Column(String, nullable=False)
#     created_at = Column(DateTime, default=func.now())

#     # Relationship
#     canteens = relationship("CanteenImageTable", back_populates="image")

#     def __repr__(self):
#         return f"<Image(id='{self.id}', name='{self.name}')>"