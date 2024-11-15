import uuid

from typing import Dict, List
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from shared.core.exceptions import DatabaseError, NotFoundError
from shared.models.canteen_model import CanteenLikeTable, CanteenTable
from shared.core.logging import get_canteen_logger

class CanteenService:
    def __init__(self, db: Session) -> None:
        """Initialize the CanteenService with a database session."""
        self.db = db
        self.logger = get_canteen_logger(__name__)
    
    def get_canteen(self, canteen_id: str) -> CanteenTable:
        """Retrieve a canteen from the database by its ID."""
        try:
            stmt = select(CanteenTable).where(CanteenTable.id == canteen_id)
            canteen = self.db.execute(stmt).scalar_one_or_none()
            if canteen is None:
                self.logger.error(f"Canteen with id {canteen_id} not found")
                raise NotFoundError(
                detail=f"Canteen with id {canteen_id} not found",
                extra={"canteen_id": canteen_id}
            )
            return canteen
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to fetch canteen: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch canteen",
                extra={"original_error": str(e)}
            ) from e


    def get_like(self, canteen_id: int, user_id: str) -> CanteenLikeTable:
        """Get the like status of a canteen by a user"""
        try:
            stmt = select(CanteenLikeTable).where(
                CanteenLikeTable.canteen_id == canteen_id,
                CanteenLikeTable.user_id == user_id
            )
            canteen_like = self.db.execute(stmt).scalar_one_or_none()
            return canteen_like
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to fetch canteen like status: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch canteen like status",
                extra={
                    "canteen_id": canteen_id,
                    "user_id": user_id,
                    "original_error": str(e)
                }
            ) from e


    def toggle_like(self, canteen_id: str, user_id: uuid.UUID) -> bool:
        """Toggle the like status of a canteen by a user"""
        existing_like = self.get_like(canteen_id, user_id)

        if existing_like:
            # If the user already liked the canteen, remove the like
            self.db.delete(existing_like)
            self.db.commit()
            return False
        else:
            # If the user has not liked the canteen yet, add a new like
            new_like = CanteenLikeTable(canteen_id=canteen_id, user_id=user_id)
            self.db.add(new_like)
            self.db.commit()
            return True


    def get_user_liked(self, user_id: uuid.UUID, canteens: List[CanteenTable]) -> Dict[str, bool]:
        canteen_ids = [canteen.id for canteen in canteens]
        stmt = select(CanteenLikeTable.canteen_id).where(
            and_(
                CanteenLikeTable.user_id == user_id,
                CanteenLikeTable.canteen_id.in_(canteen_ids)
            )
        )
        liked_canteens = self.db.execute(stmt).scalars().all()
        
        liked_canteen_ids = set(liked_canteens)
        return {canteen.id: canteen.id in liked_canteen_ids for canteen in canteens}
