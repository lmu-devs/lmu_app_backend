import uuid
from typing import List, Optional

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
    
    async def get_canteens_with_likes(
        self, 
        user_id: Optional[uuid.UUID], 
        canteen_id: Optional[str] = None
    ) -> List[CanteenTable]:
        """Retrieve canteens along with like status for a specific user in a single query."""
        try:
            # Start with base query including all needed relationships
            stmt = select(CanteenTable).options(
                selectinload(CanteenTable.location),
                selectinload(CanteenTable.opening_hours),
                selectinload(CanteenTable.images),
                selectinload(CanteenTable.status),
                selectinload(CanteenTable.likes)
            )
            
            # Filter by canteen_id if provided, otherwise use active canteens
            if canteen_id:
                stmt = stmt.where(CanteenTable.id == canteen_id)
            else:
                active_canteen_ids = [canteen.value for canteen in CanteenEnum]
                stmt = stmt.where(CanteenTable.id.in_(active_canteen_ids))

            # Add likes filtering only if user_id is provided
            if user_id:
                # Join with likes table to get user-specific likes
                stmt = stmt.outerjoin(
                    CanteenLikeTable,
                    and_(
                        CanteenTable.id == CanteenLikeTable.canteen_id,
                        CanteenLikeTable.user_id == user_id
                    )
                )
            
            result = await self.db.execute(stmt)
            canteens = result.scalars().all()
            
            if canteen_id and not canteens:
                raise NotFoundError(
                    detail=f"Canteen with id {canteen_id} not found",
                    extra={"canteen_id": canteen_id}
                )
            
            return canteens
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch canteens with likes: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch canteens with likes",
                extra={"original_error": str(e)}
            ) from e

    async def get_canteens(
        self, 
        canteen_id: Optional[str] = None, 
        user_id: Optional[uuid.UUID] = None
    ) -> List[CanteenTable]:
        """Retrieve canteens without like information."""
        # Existing implementation for cases without user
        pass  # Keep your existing implementation here if needed
    
    async def toggle_like(self, canteen_id: str, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(CanteenLikeTable, canteen_id, user_id)



