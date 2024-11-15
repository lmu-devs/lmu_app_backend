from datetime import date
from typing import List
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from shared.core.exceptions import DatabaseError, NotFoundError
from shared.models.canteen_model import CanteenLikeTable
from shared.models.menu_model import MenuDayTable, MenuDishAssociation
from shared.models.user_model import UserTable
from shared.core.logging import get_menu_logger

class MenuService:
    def __init__(self, db: Session):
        """Initialize the MenuService with a database session."""
        self.db = db
        self.logger = get_menu_logger(__name__)
        
    def get_days(
        self, 
        canteen_id: str, 
        date_from: date,
        date_to: date,
        current_user: UserTable, 
        only_liked_canteens: bool
    ) -> List[MenuDayTable]:
        """Get menu days from the database within a date range"""
        try:
            # Base query
            stmt = (
                select(MenuDayTable)
                .options(
                    joinedload(MenuDayTable.canteen),
                    joinedload(MenuDayTable.dish_associations)
                    .joinedload(MenuDishAssociation.dish)
                )
                .where(
                    MenuDayTable.date >= date_from,
                    MenuDayTable.date <= date_to
                )
            )

            # Apply filters based on parameters
            if canteen_id:
                stmt = stmt.where(MenuDayTable.canteen_id == canteen_id)
            elif only_liked_canteens and current_user:
                stmt = stmt.join(
                    CanteenLikeTable,
                    and_(
                        CanteenLikeTable.canteen_id == MenuDayTable.canteen_id,
                        CanteenLikeTable.user_id == current_user.id
                    )
                )
                
            # Execute query
            result = self.db.execute(stmt)
            menu_days = result.unique().scalars().all()
            
            if not menu_days:
                self.logger.warning(f"No menus found for {canteen_id} between {date_from} and {date_to}")
                raise NotFoundError(
                    detail="No menus found for the specified period",
                    extra={
                        "canteen_id": canteen_id, 
                        "date_from": date_from.isoformat(), 
                        "date_to": date_to.isoformat()
                    }
                )
            
            return menu_days

        except SQLAlchemyError as e:
            self.logger.error(f"Database error while fetching menus: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch menus",
                extra={"original_error": str(e)}
            ) from e
