import uuid

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager
from sqlalchemy.exc import SQLAlchemyError

from shared.core.exceptions import DatabaseError, NotFoundError
from shared.core.language import Language
from shared.core.logging import get_api_logger
from shared.models.wishlist_model import WishlistTable, WishlistImageTable, WishlistLikeTable, WishlistTranslationTable
from api.v1.core.translation_utils import apply_translation_query

logger = get_api_logger(__name__)

class WishlistService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_wishlists(self, language: Language = Language.GERMAN, wishlist_id: Optional[int] = None) -> WishlistTable:
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

    def create_wishlist(self, wishlist_data: dict) -> WishlistTable:
        try:
            # Extract nested data
            images_data = wishlist_data.pop("images", [])
            translations = wishlist_data.pop("translations", [])
            
            # Create wishlist
            new_wishlist = WishlistTable(
                status=wishlist_data["status"],
                release_date=wishlist_data.get("release_date"),
                prototype_url=wishlist_data.get("prototype_url")
            )

            
            # Add images
            for image in images_data:
                new_wishlist.images.append(WishlistImageTable(**image))
            
            # Add translations
            for translation in translations:
                new_wishlist.translations.append(
                WishlistTranslationTable(
                        language=translation["language"],
                        title=translation["title"],
                        description=translation["description"],
                        wishlist=new_wishlist
                    )
                )
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
            
            # Extract nested data
            images_data = wishlist_data.pop("images", None)
            translations = wishlist_data.pop("translations", None)
            
            # Update basic fields
            for key, value in wishlist_data.items():
                setattr(wishlist, key, value)
            
            # Update images if provided
            if images_data is not None:
                wishlist.images = []
                for image in images_data:
                    wishlist.images.append(WishlistImageTable(**image))
        
            # Update translations if provided
            if translations is not None:
                wishlist.translations = []
                for translation in translations:
                    wishlist.translations.append(
                        WishlistTranslationTable(
                            language=translation["language"],
                            title=translation["title"],
                            description=translation["description"],
                            wishlist=wishlist
                        )
                    )
            
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
        try:
            existing_like = self.db.query(WishlistLikeTable).filter(
                WishlistLikeTable.wishlist_id == wishlist_id,
                WishlistLikeTable.user_id == user_id
            ).first()

            if existing_like:
                self.db.delete(existing_like)
                self.db.commit()
                return False
            else:
                new_like = WishlistLikeTable(wishlist_id=wishlist_id, user_id=user_id)
                self.db.add(new_like)
                self.db.commit()
                return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(
                detail="Failed to toggle wishlist like",
                extra={"original_error": str(e)}
            ) 