from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, RootModel

from api.src.v2.core.models.image_model import Images
from shared.src.models import Rating
from shared.src.tables import WishlistStatus


class Wishlist(BaseModel):
    id: str
    title: str
    description: str
    content: str
    status: WishlistStatus
    release_date: Optional[datetime]
    prototype_url: Optional[str]
    rating: Rating
    images: Images
    date_updated: datetime


class Wishlists(RootModel):
    root: List[Wishlist]
