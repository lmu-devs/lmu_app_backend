from enum import Enum

from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.tables.link.link_table import LinkTable, LinkTranslationTable


# TODO: add Benifit Type to LinkBenefitTable
class BenefitType(str, Enum):
    SOFTWARE = "SOFTWARE"
    CULTURE = "CULTURE"
    TRANSPORT = "TRANSPORT"
    SHOPPING = "SHOPPING"
    LEARNING = "LEARNING"
    ONLY_LMU = "ONLY_LMU"
    ONLY_MUNICH = "ONLY_MUNICH"


class LinkBenefitTable(LinkTable):
    __tablename__ = "link_benefits"

    image_url = Column(String, nullable=True)
    types = Column(ARRAY(String), nullable=True)
    faculties = Column(ARRAY(String), nullable=True)

    translations = relationship("LinkBenefitTranslationTable", back_populates="link")


class LinkBenefitTranslationTable(LinkTranslationTable):
    __tablename__ = "link_benefit_translations"

    link_id = Column(String, ForeignKey("link_benefits.id"), primary_key=True)

    link = relationship("LinkBenefitTable", back_populates="translations")
