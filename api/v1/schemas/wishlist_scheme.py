from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from shared.core.language import Language
from shared.models.wishlist_model import WishlistStatus
from api.v1.schemas.image_scheme import Image
from api.v1.schemas.rating_scheme import Rating


class WishlistTranslation(BaseModel):
    title: str
    description: str
    language: Language

class WishlistCreate(BaseModel):
    status: WishlistStatus
    release_date: Optional[datetime] = None
    prototype_url: Optional[str] = None
    images: List[Image] = Field(default_factory=list)
    translations: List[WishlistTranslation] = Field(default_factory=list)


class WishlistUpdate(WishlistCreate):
    pass


class Wishlist(BaseModel):
    id: int
    title: str
    description: str
    status: WishlistStatus
    release_date: Optional[datetime]
    prototype_url: Optional[str]
    rating: Rating
    images: List[Image]
    created_at: datetime
    updated_at: datetime


class Wishlists(BaseModel):
    wishlists: List[Wishlist]
    
    