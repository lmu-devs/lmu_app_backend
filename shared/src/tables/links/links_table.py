from sqlalchemy import UUID, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class LinkTable(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    likes = relationship("LinkLikeTable", back_populates="link")

    @property
    def like_count(self):
        return len(self.likes)

    is_liked = False


class LinkLikeTable(Base):
    __tablename__ = "links_likes"

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    link = relationship("LinkTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_links")
