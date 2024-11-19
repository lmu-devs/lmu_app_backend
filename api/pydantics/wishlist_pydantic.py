import uuid
from typing import Optional

from shared.models.wishlist_model import WishlistTable
from api.schemas.wishlist_scheme import Wishlist
from api.schemas.rating_scheme import Rating
from api.schemas.image_scheme import Image


def wishlist_to_pydantic(wishlist: WishlistTable, user_id: Optional[uuid.UUID] = None) -> Wishlist:
    # Handle translations
    title = wishlist.title  # fallback to default title
    description = wishlist.description  # fallback to default description
    
    if wishlist.translations:
        # Use first translation found (should be filtered by language middleware)
        translation = wishlist.translations[0]
        title = translation.title
        description = translation.description

    # Handle likes
    user_likes_wishlist = None
    if user_id:
        user_likes_wishlist = any(like.user_id == user_id for like in wishlist.likes)
    
    rating = Rating(
        like_count=len(wishlist.likes),
        is_liked=user_likes_wishlist
    )
    
    # Handle images
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