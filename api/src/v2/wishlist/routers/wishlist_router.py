from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v2.core import APIKey, get_language
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_food_logger
from shared.src.enums import LanguageEnum
from shared.src.tables import UserTable

from ..models.wishlist_model import Wishlists
from ..services.wishlist_service import WishlistService

router = APIRouter()
logger = get_food_logger(__name__)


@router.get("/wishlists", response_model=Wishlists)
async def get_wishlists(
    id: int | None = None,
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
    user: UserTable = Depends(APIKey.verify_user_api_key_soft),
):
    wishlist_service = WishlistService(db, language)
    return await wishlist_service.get_wishlists(language, id, user.id if user else None)


@router.post("/wishlists/toggle-like", response_model=bool)
async def toggle_like(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key),
):
    wishlist_service = WishlistService(db)
    return await wishlist_service.toggle_like(id, user.id)
