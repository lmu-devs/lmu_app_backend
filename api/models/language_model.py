from sqlalchemy import Column, String

from shared.database import Base

class LanguageTable(Base):
    __tablename__ = "languages"
    
    country_code = Column(String, nullable=False)
    flag_emoji = Column(String, nullable=False)
    written = Column(String, nullable=False)
    
     