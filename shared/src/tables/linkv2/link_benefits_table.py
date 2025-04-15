from sqlalchemy import Column, String

from shared.src.tables.linkv2.link_table import LinkTableV2


class LinkBenefitTableV2(LinkTableV2):
    __tablename__ = "benefit_links"
    
    image_url = Column(String, nullable=True)