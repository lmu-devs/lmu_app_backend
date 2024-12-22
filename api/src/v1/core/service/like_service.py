import uuid
from typing import Any, Optional, Type

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_main_logger

logger = get_main_logger(__name__)

class LikeService:
    def __init__(self, db: Session):
        self.db = db

    def get_like(
        self, 
        like_table: Type[Any],
        entity_id: Any, 
        user_id: uuid.UUID,
        entity_id_column: str = None
    ) -> Optional[Any]:
        """
        Generic method to get a like status
        
        Args:
            like_table: The like table class (e.g., WishlistLikeTable)
            entity_id: ID of the entity (wishlist_id, dish_id, etc.)
            user_id: User ID
            entity_id_column: Name of the entity ID column (defaults to table name without 'likes' + '_id')
        """
        try:
            if entity_id_column is None:
                # Automatically generate column name (e.g., "wishlist_likes" -> "wishlist_id")
                entity_id_column = f"{like_table.__tablename__[:-6]}_id"

            stmt = (
                select(like_table)
                .where(
                    getattr(like_table, entity_id_column) == entity_id,
                    like_table.user_id == user_id
                )
            )
            
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch like status: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch like status",
                extra={"original_error": str(e)}
            )

    def toggle_like(
        self,
        like_table: Type[Any],
        entity_id: Any,
        user_id: uuid.UUID,
        entity_id_column: str = None
    ) -> bool:
        """
        Generic method to toggle like status
        
        Returns:
            bool: True if liked, False if unliked
        """
        existing_like = self.get_like(like_table, entity_id, user_id, entity_id_column)

        try:
            if existing_like:
                self.db.delete(existing_like)
                self.db.commit()
                return False
            else:
                if entity_id_column is None:
                    entity_id_column = f"{like_table.__tablename__[:-6]}_id"
                
                new_like = like_table(**{
                    entity_id_column: entity_id,
                    'user_id': user_id
                })
                self.db.add(new_like)
                self.db.commit()
                return True
                
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to toggle like status: {str(e)}")
            raise DatabaseError(
                detail="Failed to toggle like status",
                extra={"original_error": str(e)}
            )