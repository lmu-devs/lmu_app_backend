from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.tables.links.link_table import LinkTable, LinkTranslationTable


class LinkBenefitTable(LinkTable):
    __tablename__ = "link_benefits"
    
    image_url = Column(String, nullable=True)
    
    translations = relationship("LinkBenefitTranslationTable", back_populates="link")
    
class LinkBenefitTranslationTable(LinkTranslationTable):
    __tablename__ = "link_benefit_translations"
    
    link_id = Column(String, ForeignKey("link_benefits.id"), primary_key=True)
    
    link = relationship("LinkBenefitTable", back_populates="translations")
