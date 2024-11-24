from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.v1.core.api_key import APIKey
from api.v1.core.language import get_language
from api.v1.pydantics.wishlist_pydantic import wishlist_to_pydantic
from api.v1.schemas.wishlist_scheme import (Wishlist, WishlistCreate,
                                            Wishlists, WishlistUpdate)
from api.v1.services.wishlist_service import WishlistService
from shared.enums.language_enums import Language
from shared.core.logging import get_api_logger
from shared.database import get_db
from shared.models.user_model import UserTable

router = APIRouter()
logger = get_api_logger(__name__)

@router.get("/wishlists", response_model=Wishlists)
async def get_wishlists(
    id: int | None = None,
    db: Session = Depends(get_db),
    language: Language = Depends(get_language),
    user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    wishlist_service = WishlistService(db)
    wishlists = wishlist_service.get_wishlists(language, id)
    
    return Wishlists(wishlists=[
        wishlist_to_pydantic(wishlist, user.id if user else None) 
        for wishlist in wishlists
    ])
    
    
@router.post("/wishlists/toggle-like", response_model=bool)
async def toggle_wishlist_like(
    id: int,
    db: Session = Depends(get_db),
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    wishlist_service = WishlistService(db)
    return wishlist_service.toggle_like(id, user.id) 


# Wishlist System Routes

@router.post("/wishlists", response_model=Wishlist)
async def create_wishlist(
    wishlist: WishlistCreate,
    db: Session = Depends(get_db),
    authorized: bool = Depends(APIKey.verify_admin_api_key)
):
    wishlist_service = WishlistService(db)
    new_wishlist = wishlist_service.create_wishlist(wishlist.model_dump())
    return wishlist_to_pydantic(new_wishlist)


@router.put("/wishlists", response_model=Wishlist)
async def update_wishlist(
    id: int,
    wishlist: WishlistUpdate,
    db: Session = Depends(get_db),
    authorized: bool = Depends(APIKey.verify_admin_api_key)
):
    wishlist_service = WishlistService(db)
    updated_wishlist = wishlist_service.update_wishlist(id, wishlist.model_dump())
    return wishlist_to_pydantic(updated_wishlist)


@router.delete("/wishlists")
async def delete_wishlist(
    id: int,
    db: Session = Depends(get_db),
    authorized: bool = Depends(APIKey.verify_admin_api_key)
):
    wishlist_service = WishlistService(db)
    return wishlist_service.delete_wishlist(id)


