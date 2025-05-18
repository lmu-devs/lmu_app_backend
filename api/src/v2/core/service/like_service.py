import uuid
from typing import Any, Optional, Type

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_main_logger

logger = get_main_logger(__name__)


class LikeService:
    """
    Service for managing likes on various entities.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_like(
        self,
        like_table: Type[Any],
        entity_id: Any,
        user_id: uuid.UUID,
        entity_id_column: str = None,
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

            stmt = select(like_table).where(
                getattr(like_table, entity_id_column) == entity_id,
                like_table.user_id == user_id,
            )

            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch like status: {str(e)}")
            raise DatabaseError(detail="Failed to fetch like status", extra={"original_error": str(e)})

    async def toggle_like(
        self,
        like_table: Type[Any],
        entity_id: Any,
        user_id: uuid.UUID,
        entity_id_column: str = None,
    ) -> bool:
        """
        Generic method to toggle like status

        Returns:
            bool: True if liked, False if unliked
        """
        existing_like = await self.get_like(like_table, entity_id, user_id, entity_id_column)

        try:
            if existing_like:
                await self.db.delete(existing_like)
                await self.db.commit()
                return False
            else:
                if entity_id_column is None:
                    entity_id_column = f"{like_table.__tablename__[:-6]}_id"

                new_like = like_table(**{entity_id_column: entity_id, "user_id": user_id})
                self.db.add(new_like)
                await self.db.commit()
                return True

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Failed to toggle like status: {str(e)}")
            raise DatabaseError(detail="Failed to toggle like status", extra={"original_error": str(e)})

    async def get_user_likes(
        self,
        like_table: Type[Any],
        user_id: uuid.UUID,
        entity_id_column: str = None,
    ) -> list[Any]:
        """
        Get all likes for a specific user and like table

        Args:
            like_table: The like table class (e.g., WishlistLikeTable)
            user_id: User ID
            entity_id_column: Name of the entity ID column (defaults to table name without 'likes' + '_id')

        Returns:
            list: List of entity IDs that the user has liked
        """
        try:
            if entity_id_column is None:
                entity_id_column = f"{like_table.__tablename__[:-6]}_id"

            stmt = select(getattr(like_table, entity_id_column)).where(like_table.user_id == user_id)

            result = await self.db.execute(stmt)
            return result.scalars().all()

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch user likes: {str(e)}")
            raise DatabaseError(detail="Failed to fetch user likes", extra={"original_error": str(e)})

    async def get_like_counts(
        self,
        like_table: Type[Any],
        entity_ids: list[Any],
        entity_id_column: str = None,
    ) -> dict[Any, int]:
        """
        Get like counts for multiple entities at once

        Args:
            like_table: The like table class (e.g., WishlistLikeTable)
            entity_ids: List of entity IDs to get counts for
            entity_id_column: Name of the entity ID column (defaults to table name without 'likes' + '_id')

        Returns:
            dict: Mapping of entity IDs to their like counts
        """
        try:
            if entity_id_column is None:
                entity_id_column = f"{like_table.__tablename__[:-6]}_id"

            entity_col = getattr(like_table, entity_id_column)
            stmt = (
                select(entity_col, func.count(like_table.user_id).label("like_count"))
                .where(entity_col.in_(entity_ids))
                .group_by(entity_col)
            )

            result = await self.db.execute(stmt)
            counts = {entity_id: count for entity_id, count in result.all()}

            # Ensure all requested entity IDs have an entry in the result dictionary
            return {entity_id: counts.get(entity_id, 0) for entity_id in entity_ids}

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch like counts: {str(e)}")
            raise DatabaseError(detail="Failed to fetch like counts", extra={"original_error": str(e)})
