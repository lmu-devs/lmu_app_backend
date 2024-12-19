import uuid
from typing import Optional

from shared.src.tables import WishlistTable
from ..schemas import Wishlist
from ...core import Rating, Image


def wishlist_to_pydantic(wishlist: WishlistTable, user_id: Optional[uuid.UUID] = None) -> Wishlist:
    
    title = wishlist.translations[0].title if wishlist.translations else "not translated"
    description = wishlist.translations[0].description if wishlist.translations else "not translated"
    
    # Handle likes
    user_likes_wishlist = None
    if user_id:
        user_likes_wishlist = any(like.user_id == user_id for like in wishlist.likes)
    
    rating = Rating(
        like_count=len(wishlist.likes),
        is_liked=user_likes_wishlist
    )
    
    images = [
        Image(url=image.url, name=image.name)
        for image in wishlist.images
    ]

    return Wishlist(
        id=wishlist.id,
        title=title,
        description=description,
        status=wishlist.status,
        release_date=wishlist.release_date,
        prototype_url=wishlist.prototype_url,
        rating=rating,
        images=images,
        created_at=wishlist.created_at,
        updated_at=wishlist.updated_at
    ) 