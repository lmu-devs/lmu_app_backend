import uuid
from typing import Optional

from shared.core.language import Language
from shared.models.wishlist_model import WishlistTable
from api.schemas.wishlist_scheme import Wishlist
from api.schemas.rating_scheme import Rating
from api.schemas.image_scheme import Image
from api.utils.translation_utils import get_translation


def _get_translation(wishlist: WishlistTable, language: Language) -> tuple[str, str]:
    title = get_translation(
        wishlist.translations,
        language,
        lambda t: t.language,
        lambda t: t.title
    )
    
    description = get_translation(
        wishlist.translations,
        language,
        lambda t: t.language,
        lambda t: t.description
    )
    
    return title, description


def wishlist_to_pydantic(wishlist: WishlistTable, language: Language = Language.GERMAN, user_id: Optional[uuid.UUID] = None) -> Wishlist:
    title, description = _get_translation(wishlist, language)
    
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