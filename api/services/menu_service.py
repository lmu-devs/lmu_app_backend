from datetime import date
from typing import List
from sqlalchemy import and_, select, case
from sqlalchemy.orm import Session, contains_eager
from sqlalchemy.exc import SQLAlchemyError

from shared.enums.language_enums import Language
from shared.core.exceptions import DatabaseError, NotFoundError
from shared.models.canteen_model import CanteenLikeTable
from shared.models.menu_model import MenuDayTable, MenuDishAssociation
from shared.models.user_model import UserTable
from shared.models.dish_model import DishTable, DishTranslationTable
from shared.core.logging import get_menu_logger

logger = get_menu_logger(__name__)
class MenuService:
    def __init__(self, db: Session):
        """Initialize the MenuService with a database session."""
        self.db = db
        

    def get_days(
        self, 
        canteen_id: str, 
        date_from: date,
        date_to: date,
        current_user: UserTable, 
        only_liked_canteens: bool,
        language: Language = Language.GERMAN
    ) -> List[MenuDayTable]:
        """Get menu days from the database within a date range"""
        try:
            # Base query
            stmt = (
                select(MenuDayTable)
                .join(MenuDayTable.canteen)
                .join(MenuDayTable.dish_associations)
                .join(MenuDishAssociation.dish)
                .outerjoin(DishTable.translations)
            )
            
            # Apply translation query - modify to use the already joined translations
            stmt = (
                stmt
                .options(
                    contains_eager(MenuDayTable.canteen),
                    contains_eager(MenuDayTable.dish_associations)
                    .contains_eager(MenuDishAssociation.dish)
                    .contains_eager(DishTable.translations)
                )
                .order_by(
                    DishTable.id,
                    case(
                        (DishTranslationTable.language == language.value, 1),
                        (DishTranslationTable.language == Language.GERMAN.value, 2),
                        else_=3
                    )
                )
            )
            
            # Add date filters
            stmt = stmt.where(
                MenuDayTable.date >= date_from,
                MenuDayTable.date <= date_to
            )
            logger.info(f"Fetching menu days for canteen {canteen_id} from {date_from} to {date_to} with language {language.value}, user_id: {current_user.id if current_user else None}, only_liked_canteens: {only_liked_canteens}")

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
                logger.warning(f"No menus found for {canteen_id} between {date_from} and {date_to}")
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
            logger.error(f"Database error while fetching menus: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch menus",
                extra={"original_error": str(e)}
            ) from e
