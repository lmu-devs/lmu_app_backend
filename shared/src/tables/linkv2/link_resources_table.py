from enum import Enum
from sqlalchemy import ARRAY, Column, String

from shared.src.tables.linkv2.link_table import LinkTableV2


class LinkType(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"

class LinkResourceTableV2(LinkTableV2):
    __tablename__ = "resource_links"
    
    types = Column(ARRAY(String), nullable=False)