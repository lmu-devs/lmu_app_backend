from enum import Enum

from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.language_table import LanguageTable
from shared.src.tables.links.link_table import LinkTable, LinkTranslationTable


class LinkType(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"

class LinkResourceTable(LinkTable):
    __tablename__ = "link_resources"
    
    types = Column(ARRAY(String), nullable=False)
    
    translations = relationship("LinkResourceTranslationTable", back_populates="link")
    
class LinkResourceTranslationTable(LinkTranslationTable):
    __tablename__ = "link_resource_translations"
    
    link_id = Column(String, ForeignKey("link_resources.id"), primary_key=True)
    
    link = relationship("LinkResourceTable", back_populates="translations")
