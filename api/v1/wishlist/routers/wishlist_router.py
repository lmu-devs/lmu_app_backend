from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.v1.core import APIKey, get_language
from shared.core.logging import get_food_api_logger
from shared.database import get_db
from shared.enums.language_enums import LanguageEnum
from shared.tables.user_table import UserTable

from ..pydantics.wishlist_pydantic import wishlist_to_pydantic
from ..schemas.wishlist_scheme import (Wishlist, WishlistCreate, Wishlists,
                                       WishlistUpdate)
from ..services.wishlist_service import WishlistService

router = APIRouter()
logger = get_food_api_logger(__name__)

@router.get("/wishlists", response_model=Wishlists)
async def get_wishlists(
    id: int | None = None,
    db: Session = Depends(get_db),
    language: LanguageEnum = Depends(get_language),
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


