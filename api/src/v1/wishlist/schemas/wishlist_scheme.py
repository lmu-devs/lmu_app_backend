from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from shared.src.enums import LanguageEnum
from shared.src.tables import WishlistStatus
from shared.src.models import Image, Rating


class WishlistTranslation(BaseModel):
    title: str
    description_short: str
    description: str
    language: LanguageEnum

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
    description_short: str
    status: WishlistStatus
    release_date: Optional[datetime]
    prototype_url: Optional[str]
    rating: Rating
    images: List[Image]
    created_at: datetime
    updated_at: datetime


class Wishlists(BaseModel):
    wishlists: List[Wishlist]
    
    