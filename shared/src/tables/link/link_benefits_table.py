from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.tables.link.link_table import LinkTable, LinkTranslationTable


# TODO: add Benifit Type to LinkBenefitTable
class BenefitType:
    software: str = "SOFTWARE"
    culture: str = "CULTURE"
    transport: str = "TRANSPORT"
    shopping: str = "SHOPPING"
    leanring: str = "LEARNING"
    only_lmu: str = "ONLY_LMU"
    only_munich: str = "ONLY_MUNICH"


class LinkBenefitTable(LinkTable):
    __tablename__ = "link_benefits"

    image_url = Column(String, nullable=True)

    translations = relationship("LinkBenefitTranslationTable", back_populates="link")


class LinkBenefitTranslationTable(LinkTranslationTable):
    __tablename__ = "link_benefit_translations"

    link_id = Column(String, ForeignKey("link_benefits.id"), primary_key=True)

    link = relationship("LinkBenefitTable", back_populates="translations")
