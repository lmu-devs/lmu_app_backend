import uuid
from typing import Any, List, Type

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_main_logger


logger = get_main_logger(__name__)

class LikeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_likes(
        self, 
        like_table: Type[Any],
        user_id: uuid.UUID
    ) -> List[Any]:
        """
        Generic method to get all like statuses for a user.
        
        Args:
            like_table: The like table class (e.g., CanteenLikeTable, SportCourseLikeTable)
            user_id: User ID
            
        Returns:
            List of like instances.
        """
        try:
            stmt = select(like_table).where(like_table.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch likes: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch likes",
                extra={"original_error": str(e)}
            )

    async def toggle_like(
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
        existing_like = await self.db.execute(
            select(like_table).where(
                getattr(like_table, entity_id_column or f"{like_table.__tablename__[:-6]}_id") == entity_id,
                like_table.user_id == user_id
            )
        )
        existing_like = existing_like.scalar_one_or_none()

        try:
            if existing_like:
                await self.db.delete(existing_like)
                await self.db.commit()
                return False
            else:
                if entity_id_column is None:
                    entity_id_column = f"{like_table.__tablename__[:-6]}_id"
                
                new_like = like_table(**{
                    entity_id_column: entity_id,
                    'user_id': user_id
                })
                self.db.add(new_like)
                await self.db.commit()
                return True
                
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Failed to toggle like status: {str(e)}")
            raise DatabaseError(
                detail="Failed to toggle like status",
                extra={"original_error": str(e)}
            )