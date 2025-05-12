from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from shared.src.enums import LanguageEnum
from shared.src.models import Images, Rating
from shared.src.tables import WishlistStatus


class WishlistTranslation(BaseModel):
    title: str
    description_short: str
    description: str
    language: LanguageEnum


class Wishlist(BaseModel):
    id: int
    title: str
    description: str
    description_short: str
    status: WishlistStatus
    release_date: Optional[datetime]
    prototype_url: Optional[str]
    rating: Rating
    images: Images
    created_at: datetime
    updated_at: datetime


class Wishlists(BaseModel):
    wishlists: List[Wishlist]
