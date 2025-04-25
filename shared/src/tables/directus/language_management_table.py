from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from shared.src.core.database import Base

class LanguageManagementTable(Base):
    __tablename__ = "languages"
    
    code = Column(String(5), primary_key=True)  # Language code (e.g., 'en-US', 'de')
    name = Column(String(50), nullable=False)    # Language name (e.g., 'English', 'German')
    direction = Column(String(3), nullable=False, default="LTR")  # Text direction (LTR or RTL)
    icon = Column(String, nullable=True)  # Optional icon/flag for the language
    is_default = Column(Boolean, nullable=False, default=False)  # Whether this is the default language
    is_enabled = Column(Boolean, nullable=False, default=True)  # Whether the language is active