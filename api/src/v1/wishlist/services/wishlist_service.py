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
from shared.src.tables import WishlistImageTable, WishlistLikeTable, WishlistTable, WishlistTranslationTable


logger = get_food_logger(__name__)

class WishlistService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.like_service = LikeService(db)
    async def get_wishlists(self, language: LanguageEnum = LanguageEnum.GERMAN, wishlist_id: Optional[int] = None) -> WishlistTable:
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
            
            query = apply_translation_query(base_query=query, model=WishlistTable, translation_model=WishlistTranslationTable, language=language)

            if wishlist_id:
                query = query.filter(WishlistTable.id == wishlist_id)
            
            result = await self.db.execute(query)
            wishlists = result.scalars().unique().all()
            
            if not wishlists:
                raise NotFoundError(
                    detail="No wishlists found",
                    extra={"wishlist_id": wishlist_id}
                )
            return wishlists
        except SQLAlchemyError as e:
            raise DatabaseError(
                detail="Failed to fetch wishlists",
                extra={"original_error": str(e)}
            )

    def _set_translations(self, wishlist: WishlistTable, translations: list) -> None:
        wishlist.translations = [
            WishlistTranslationTable(
                language=t["language"],
                title=t["title"],
                description=t["description"],
                description_short=t["description_short"],
                wishlist=wishlist
            ) for t in translations
        ]

    def _set_images(self, wishlist: WishlistTable, images: list) -> None:
        wishlist.images = [WishlistImageTable(**image) for image in images]

    async def create_wishlist(self, wishlist_data: dict) -> WishlistTable:
        try:
            # Extract nested data
            images_data = wishlist_data.pop("images", [])
            translations = wishlist_data.pop("translations", [])
            
            # Create wishlist
            new_wishlist = WishlistTable(**wishlist_data)
            
            # Add images and translations
            self._set_images(new_wishlist, images_data)
            self._set_translations(new_wishlist, translations)
            
            self.db.add(new_wishlist)
            await self.db.commit()
            
            # Reload the wishlist with all relationships
            result = await self.get_wishlists(wishlist_id=new_wishlist.id)
            return result[0]
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseError(
                detail="Failed to create wishlist",
                extra={"original_error": str(e)}
            )

    async def update_wishlist(self, wishlist_id: int, wishlist_data: dict) -> WishlistTable:
        try:
            wishlist = (await self.get_wishlists(wishlist_id=wishlist_id))[0]
            
            # Extract nested data
            images_data = wishlist_data.pop("images", None)
            translations = wishlist_data.pop("translations", None)
            
            # Update basic fields
            for key, value in wishlist_data.items():
                setattr(wishlist, key, value)
            
            # Update images and translations if provided
            if images_data is not None:
                self._set_images(wishlist, images_data)
            if translations is not None:
                self._set_translations(wishlist, translations)
            
            await self.db.commit()
            
            result = await self.get_wishlists(wishlist_id=wishlist_id)
            return result[0]
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseError(
                detail="Failed to update wishlist",
                extra={"original_error": str(e)}
            )

    async def delete_wishlist(self, wishlist_id: int) -> bool:
        try:
            wishlist = (await self.get_wishlists(wishlist_id=wishlist_id))[0]
            await self.db.delete(wishlist)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseError(
                detail="Failed to delete wishlist",
                extra={"original_error": str(e)}
            )

    async def toggle_like(self, wishlist_id: int, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(WishlistLikeTable, wishlist_id, user_id)