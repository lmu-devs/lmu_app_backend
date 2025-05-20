import enum

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.image_table import ImageTable
from shared.src.tables.language_table import LanguageTable


class WishlistStatus(str, enum.Enum):
    NONE = "NONE"
    HIDDEN = "HIDDEN"
    DEVELOPMENT = "DEVELOPMENT"
    BETA = "BETA"
    DONE = "DONE"


class WishlistTable(Base):
    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(WishlistStatus), nullable=False)
    release_date = Column(DateTime, nullable=True)
    prototype_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    images = relationship("WishlistImageTable", back_populates="wishlist", cascade="all, delete-orphan")
    likes = relationship("WishlistLikeTable", back_populates="wishlist", cascade="all, delete-orphan")
    translations = relationship(
        "WishlistTranslationTable",
        back_populates="wishlist",
        cascade="all, delete-orphan",
    )

    @property
    def like_count(self):
        return len(self.likes)


class WishlistImageTable(ImageTable, Base):
    __tablename__ = "wishlist_images"

    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False)

    wishlist = relationship("WishlistTable", back_populates="images")

    def __repr__(self):
        return f"WishlistImageTable(id={self.id}, url={self.url}, name={self.name}, created_at={self.created_at}, updated_at={self.updated_at})"


class WishlistLikeTable(Base):
    __tablename__ = "wishlist_likes"

    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    wishlist = relationship("WishlistTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_wishlists")


class WishlistTranslationTable(LanguageTable):
    __tablename__ = "wishlist_translations"

    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    description_short = Column(String, nullable=False)

    wishlist = relationship("WishlistTable", back_populates="translations")
