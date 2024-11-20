import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship

from shared.database import Base
from shared.models.image_model import ImageTable
from shared.models.language_model import LanguageTable


class WishlistStatus(str, enum.Enum):
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
    translations = relationship("WishlistTranslationTable", back_populates="wishlist", cascade="all, delete-orphan")


class WishlistImageTable(ImageTable, Base):
    __tablename__ = "wishlist_images"
    
    wishlist_id = Column(Integer, ForeignKey("wishlists.id"), nullable=False)
    
    wishlist = relationship("WishlistTable", back_populates="images")


class WishlistLikeTable(Base):
    __tablename__ = "wishlist_likes"

    wishlist_id = Column(Integer, ForeignKey("wishlists.id"), primary_key=True)
    user_id = Column(ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    wishlist = relationship("WishlistTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_wishlists") 
    

class WishlistTranslationTable(LanguageTable, Base):
    __tablename__ = "wishlist_translations"
    
    wishlist_id = Column(Integer, ForeignKey("wishlists.id"), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    
    wishlist = relationship("WishlistTable", back_populates="translations")
    
    
