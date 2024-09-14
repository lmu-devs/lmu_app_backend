from pydantic import BaseModel
from sqlalchemy import Column, String

from api.database import Base


class LanguageDto(BaseModel):
    country_code: str
    flag_emoji: str
    written: float
    
    
### Database Models ###


class Language(Base):
    __tablename__ = "languages"
    
    country_code = Column(String, nullable=False)
    flag_emoji = Column(String, nullable=False)
    written = Column(String, nullable=False)
    
     