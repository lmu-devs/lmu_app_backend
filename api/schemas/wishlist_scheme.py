from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

from api.schemas.image_scheme import Image
from api.schemas.rating_scheme import Rating
from shared.models.wishlist_model import WishlistStatus


class WishlistCreate(BaseModel):
    title: str
    description: str
    status: WishlistStatus
    release_date: Optional[datetime] = None
    prototype_url: Optional[str] = None
    images: List[Image] = []
    translations: Dict[str, Dict[str, str]] = {}


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