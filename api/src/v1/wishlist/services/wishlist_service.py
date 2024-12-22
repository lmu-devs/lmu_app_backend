import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, contains_eager

from shared.src.core.exceptions import DatabaseError, NotFoundError
from shared.src.core.logging import get_food_logger
from shared.src.enums import LanguageEnum
from shared.src.tables import WishlistImageTable, WishlistLikeTable, WishlistTable, WishlistTranslationTable

from api.src.v1.core.service.like_service import BaseLikeService
from api.src.v1.core.translation_utils import apply_translation_query

logger = get_food_logger(__name__)

class WishlistService:
    def __init__(self, db: Session):
        self.db = db
        self.like_service = BaseLikeService(db)
    def get_wishlists(self, language: LanguageEnum = LanguageEnum.GERMAN, wishlist_id: Optional[int] = None) -> WishlistTable:
        try:
            query = (
                select(WishlistTable)
                .outerjoin(WishlistTable.images)
                .outerjoin(WishlistTable.likes)
                .options(
                    contains_eager(WishlistTable.images),
                    contains_eager(WishlistTable.likes)
                )
            )
            
            query = apply_translation_query(base_query=query, model=WishlistTable, translation_model=WishlistTranslationTable, language=language)

            if wishlist_id:
                query = query.filter(WishlistTable.id == wishlist_id)
            
            wishlists = self.db.execute(query).scalars().unique().all()
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

    def create_wishlist(self, wishlist_data: dict) -> WishlistTable:
        try:
            # Create wishlist
            new_wishlist = WishlistTable(**wishlist_data)
            
            # Extract nested data
            images_data = wishlist_data.pop("images", [])
            translations = wishlist_data.pop("translations", [])
            
            # Add images and translations
            self._set_images(new_wishlist, images_data)
            self._set_translations(new_wishlist, translations)
            
            self.db.add(new_wishlist)
            self.db.commit()
            self.db.refresh(new_wishlist)
            return new_wishlist
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to create wishlist",
                extra={"original_error": str(e)}
            )

    def update_wishlist(self, wishlist_id: int, wishlist_data: dict) -> WishlistTable:
        try:
            wishlist = self.get_wishlists(wishlist_id=wishlist_id)[0]
            
            
            # Update basic fields
            for key, value in wishlist_data.items():
                setattr(wishlist, key, value)
            
            # Extract nested data
            images_data = wishlist_data.pop("images", None)
            translations = wishlist_data.pop("translations", None)
            
            # Update images and translations if provided
            if images_data is not None:
                self._set_images(wishlist, images_data)
            if translations is not None:
                self._set_translations(wishlist, translations)
            
            self.db.commit()
            self.db.refresh(wishlist)
            return wishlist
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to update wishlist",
                extra={"original_error": str(e)}
            )

    def delete_wishlist(self, wishlist_id: int) -> bool:
        try:
            wishlist = self.get_wishlists(wishlist_id=wishlist_id)[0]
            self.db.delete(wishlist)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to delete wishlist",
                extra={"original_error": str(e)}
            )

    def toggle_like(self, wishlist_id: int, user_id: uuid.UUID) -> bool:
            return self.like_service.toggle_like(WishlistLikeTable, wishlist_id, user_id)