from enum import Enum

from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.tables.like_table import LikeTable
from shared.src.tables.link.link_table import LinkTable, LinkTranslationTable


class LinkType(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"


class LinkResourceTable(LinkTable):
    __tablename__ = "link_resources"

    types = Column(ARRAY(String), nullable=False)
    faculties = Column(ARRAY(String), nullable=True)

    translations = relationship("LinkResourceTranslationTable", back_populates="link")
    likes = relationship("LinkResourceLikeTable", back_populates="link")

    @property
    def like_count(self):
        return len(self.likes)

    is_liked = False


class LinkResourceTranslationTable(LinkTranslationTable):
    __tablename__ = "link_resource_translations"

    link_resource_id = Column(String, ForeignKey("link_resources.id"), primary_key=True)

    link = relationship("LinkResourceTable", back_populates="translations")


class LinkResourceLikeTable(LikeTable):
    __tablename__ = "link_resource_likes"

    link_resource_id = Column(String, ForeignKey("link_resources.id", ondelete="CASCADE"), primary_key=True)

    link = relationship("LinkResourceTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_link_resources")
