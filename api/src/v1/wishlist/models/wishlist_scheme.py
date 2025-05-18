import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from shared.src.enums import LanguageEnum
from shared.src.models import Images, Rating
from shared.src.tables import WishlistStatus
from shared.src.tables.wishlist.wishlist_table import WishlistTable


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

    @classmethod
    def from_table(cls, wishlist: WishlistTable, user_id: Optional[uuid.UUID] = None) -> "Wishlist":
        title = wishlist.translations[0].title if wishlist.translations else "not translated"
        description = wishlist.translations[0].description if wishlist.translations else "not translated"
        description_short = wishlist.translations[0].description_short if wishlist.translations else "not translated"
        # Handle likes
        user_likes_wishlist = None
        if user_id:
            # TODO: This is a temporary solution, we need to use a more efficient way to check if the user has liked the wishlist
            user_likes_wishlist = any(like.user_id == user_id for like in wishlist.likes)

        rating = Rating(like_count=len(wishlist.likes), is_liked=user_likes_wishlist)

        images = Images.from_table(wishlist.images)

        return Wishlist(
            id=wishlist.id,
            title=title,
            description=description,
            description_short=description_short,
            status=wishlist.status,
            release_date=wishlist.release_date,
            prototype_url=wishlist.prototype_url,
            rating=rating,
            images=images,
            created_at=wishlist.created_at,
            updated_at=wishlist.updated_at,
        )


class Wishlists(BaseModel):
    wishlists: List[Wishlist]
