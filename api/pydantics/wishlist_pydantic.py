import uuid
from typing import Optional

from shared.core.language import Language
from shared.models.wishlist_model import WishlistTable
from api.schemas.wishlist_scheme import Wishlist
from api.schemas.rating_scheme import Rating
from api.schemas.image_scheme import Image


def _get_translation(wishlist: WishlistTable, language: Language) -> tuple[str, str]:
    title = "not translated"
    description = "not translated"
    
    # Try to find translation in requested language
    translation = next(
        (t for t in wishlist.translations if t.language == language.value),
        None
    )
    
    # If not found, try German
    if not translation and language != Language.GERMAN:
        translation = next(
            (t for t in wishlist.translations if t.language == Language.GERMAN.value),
            None
        )
    
    # If still not found, use first available translation
    if not translation and wishlist.translations:
        translation = wishlist.translations[0]
    
    # Use translation if found
    if translation:
        title = translation.title
        description = translation.description
        
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