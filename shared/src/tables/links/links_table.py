from enum import Enum

from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.language_table import LanguageTable


class LinkType(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"

class LinkTable(Base):
    __tablename__ = "links"
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    favicon_url = Column(String, nullable=True)
    types = Column(ARRAY(String), nullable=False)
    
    translations = relationship("LinkTranslationTable", back_populates="link")
    
class LinkTranslationTable(LanguageTable, Base):
    __tablename__ = "link_translations"
    
    link_id = Column(String, ForeignKey("links.id"), primary_key=True)
    aliases = Column(ARRAY(String), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    link = relationship("LinkTable", back_populates="translations")
