import uuid
from typing import Dict, List

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.src.v1.core.service.like_service import LikeService
from shared.src.core.exceptions import DatabaseError, NotFoundError
from shared.src.core.logging import get_food_logger
from shared.src.enums import CanteenEnum
from shared.src.tables import CanteenLikeTable, CanteenTable


logger = get_food_logger(__name__)



class CanteenService:
    def __init__(self, db: AsyncSession) -> None:
        """Initialize the CanteenService with a database session."""
        self.db = db
        self.like_service = LikeService(db)
    
    async def get_canteen(self, canteen_id: str) -> CanteenTable:
        """Retrieve a canteen from the database by its ID."""
        try:
            stmt = (
                select(CanteenTable)
                .options(
                    selectinload(CanteenTable.location),
                    selectinload(CanteenTable.opening_hours),
                    selectinload(CanteenTable.likes),
                    selectinload(CanteenTable.images),
                    selectinload(CanteenTable.status),
                )
                .where(CanteenTable.id == canteen_id)
            )
            result = await self.db.execute(stmt)
            canteen = result.scalar_one_or_none()
            if canteen is None:
                logger.error(f"Canteen with id {canteen_id} not found")
                raise NotFoundError(
                    detail=f"Canteen with id {canteen_id} not found",
                    extra={"canteen_id": canteen_id}
                )
            return canteen
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch canteen: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch canteen",
                extra={"original_error": str(e)}
            ) from e
            
    
    async def get_canteens(self, canteen_id: str = None) -> List[CanteenTable]:
        """Retrieve canteens from the database.
        
        Args:
            canteen_id: Optional specific canteen ID to fetch. If None, fetches all active canteens.
        """
        try:
            stmt = (
                select(CanteenTable)
                .options(
                    selectinload(CanteenTable.location),
                    selectinload(CanteenTable.opening_hours),
                    selectinload(CanteenTable.likes),
                    selectinload(CanteenTable.images),
                    selectinload(CanteenTable.status),
                )
            )

            if canteen_id:
                stmt = stmt.where(CanteenTable.id == canteen_id)
            else:
                active_canteen_ids = [canteen.value for canteen in CanteenEnum]
                stmt = stmt.where(CanteenTable.id.in_(active_canteen_ids))

            result = await self.db.execute(stmt)
            canteens = result.scalars().all()

            if canteen_id and not canteens:
                logger.error(f"Canteen with id {canteen_id} not found")
                raise NotFoundError(
                    detail=f"Canteen with id {canteen_id} not found",
                    extra={"canteen_id": canteen_id}
                )

            return canteens

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch canteen(s): {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch canteen(s)",
                extra={"original_error": str(e)}
            ) from e


    async def get_like(self, canteen_id: int, user_id: str) -> CanteenLikeTable:
        return await self.like_service.get_like(CanteenLikeTable, canteen_id, user_id)


    async def toggle_like(self, canteen_id: str, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(CanteenLikeTable, canteen_id, user_id)


    async def get_user_liked(self, user_id: uuid.UUID) -> Dict[str, bool]:
        active_canteen_ids = [canteen.value for canteen in CanteenEnum]
        
        stmt = select(CanteenLikeTable.canteen_id).where(
            and_(
                CanteenLikeTable.user_id == user_id,
                CanteenLikeTable.canteen_id.in_(active_canteen_ids)
            )
        )
        result = await self.db.execute(stmt)
        liked_canteens = result.scalars().all()
        
        likes = {canteen_id: False for canteen_id in active_canteen_ids}
        for canteen_id in liked_canteens:
            likes[canteen_id] = True
            
        return likes


