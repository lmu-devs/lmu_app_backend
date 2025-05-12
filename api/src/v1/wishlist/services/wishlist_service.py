import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from api.src.v1.core.service.like_service import LikeService
from api.src.v1.core.translation_utils import apply_translation_query
from shared.src.core.exceptions import DatabaseError, NotFoundError
from shared.src.core.logging import get_food_logger
from shared.src.enums import LanguageEnum
from shared.src.tables import (
    WishlistImageTable,
    WishlistLikeTable,
    WishlistTable,
    WishlistTranslationTable,
)

logger = get_food_logger(__name__)


class WishlistService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.like_service = LikeService(db)

    async def get_wishlists(
        self,
        language: LanguageEnum = LanguageEnum.GERMAN,
        wishlist_id: Optional[int] = None,
    ) -> WishlistTable:
        try:
            query = (
                select(WishlistTable)
                .outerjoin(WishlistTable.images)
                .outerjoin(WishlistTable.likes)
                .options(
                    contains_eager(WishlistTable.images),
                    contains_eager(WishlistTable.likes),
                )
            )

            query = apply_translation_query(
                base_query=query,
                model=WishlistTable,
                translation_model=WishlistTranslationTable,
                language=language,
            )

            if wishlist_id:
                query = query.filter(WishlistTable.id == wishlist_id)

            result = await self.db.execute(query)
            wishlists = result.scalars().unique().all()

            if not wishlists:
                raise NotFoundError(detail="No wishlists found", extra={"wishlist_id": wishlist_id})
            return wishlists
        except SQLAlchemyError as e:
            raise DatabaseError(detail="Failed to fetch wishlists", extra={"original_error": str(e)})

    def _set_translations(self, wishlist: WishlistTable, translations: list) -> None:
        wishlist.translations = [
            WishlistTranslationTable(
                language=t["language"],
                title=t["title"],
                description=t["description"],
                description_short=t["description_short"],
                wishlist=wishlist,
            )
            for t in translations
        ]

    def _set_images(self, wishlist: WishlistTable, images: list) -> None:
        wishlist.images = [WishlistImageTable(**image) for image in images]

    async def toggle_like(self, wishlist_id: int, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(WishlistLikeTable, wishlist_id, user_id)
