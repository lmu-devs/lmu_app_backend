import uuid
from typing import Dict, List

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

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
            
    
    async def get_all_active_canteens(self) -> List[CanteenTable]:
        """Retrieve all canteens that are defined in the CanteenID enum."""
        try:
            active_canteen_ids = [canteen.value for canteen in CanteenEnum]
            stmt = (
                select(CanteenTable)
                .options(
                    selectinload(CanteenTable.location),
                    selectinload(CanteenTable.opening_hours),
                    selectinload(CanteenTable.likes),
                    selectinload(CanteenTable.images),
                    selectinload(CanteenTable.status),
                )
                .where(CanteenTable.id.in_(active_canteen_ids))
            )
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch active canteens: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch active canteens",
                extra={"original_error": str(e)}
            ) from e


    async def get_like(self, canteen_id: int, user_id: str) -> CanteenLikeTable:
        return await self.like_service.get_like(CanteenLikeTable, canteen_id, user_id)


    async def toggle_like(self, canteen_id: str, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(CanteenLikeTable, canteen_id, user_id)


    async def get_user_liked(self, user_id: uuid.UUID, canteens: List[CanteenTable]) -> Dict[str, bool]:
        canteen_ids = [canteen.id for canteen in canteens]
        stmt = select(CanteenLikeTable.canteen_id).where(
            and_(
                CanteenLikeTable.user_id == user_id,
                CanteenLikeTable.canteen_id.in_(canteen_ids)
            )
        )
        result = await self.db.execute(stmt)
        liked_canteens = result.scalars().all()
        
        liked_canteen_ids = set(liked_canteens)
        return {canteen.id: canteen.id in liked_canteen_ids for canteen in canteens}


