import uuid
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from shared.src.core.exceptions import DatabaseError, NotFoundError
from shared.src.core.logging import get_food_logger
from shared.src.enums import LanguageEnum
from shared.src.tables import CanteenTable, DishLikeTable, DishTable, DishTranslationTable, MenuDayTable, MenuDishAssociation

from ...core.translation_utils import apply_translation_query

logger = get_food_logger(__name__)

class DishService:
    def __init__(self, db: Session):
        """Initialize the DishService with a database session."""
        self.db = db

    def get_dishes(
        self, 
        dish_id: Optional[int] = None, 
        user_id: Optional[uuid.UUID] = None,
        only_liked: bool = False,
        language: LanguageEnum = LanguageEnum.GERMAN    
    ) -> List[DishTable]:
        """
        Get dishes from the database.
        If dish_id is provided, return a list with only that dish.
        If user_id and only_liked are provided, return liked dishes for that user.
        Otherwise, return all dishes.
        """
        try:
            # Base query with translations
            stmt = (
                select(DishTable)
            )
            
            stmt = apply_translation_query(base_query=stmt, model=DishTable, translation_model=DishTranslationTable, language=language)

            # Add filters based on parameters
            if dish_id:
                stmt = stmt.where(DishTable.id == dish_id)
                
            if user_id and only_liked:
                # Return only dishes liked by the user
                stmt = (
                    stmt
                    .join(DishLikeTable)
                    .where(DishLikeTable.user_id == user_id)
                )
            elif user_id:
                # Left join with DishLikeTable to get like status for the user
                stmt = (
                    stmt
                    .outerjoin(
                        DishLikeTable,
                        and_(
                            DishLikeTable.dish_id == DishTable.id,
                            DishLikeTable.user_id == user_id
                        )
                    )
                )

            dishes = self.db.execute(stmt).unique().scalars().all()
            

            if not dishes:
                raise NotFoundError(
                    detail=f"No dishes found with the specified criteria",
                    extra={"dish_id": dish_id}
                )
            logger.info(f"Found {len(dishes)} dishes matching criteria. dish_id: {dish_id}, user_id: {user_id}, only_liked: {only_liked}")
            return dishes

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch dishes: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch dishes",
                extra={"original_error": str(e)}
            )
    


    def get_like(self, dish_id: int, user_id: uuid.UUID) -> DishLikeTable:
        """Get the like status of a dish by a user"""
        try:
            stmt = (
                select(DishLikeTable)
                .where(
                    DishLikeTable.dish_id == dish_id,
                    DishLikeTable.user_id == user_id
                )
            )
            
            result = self.db.execute(stmt)
            dish_like = result.scalar_one_or_none()
            
            
            return dish_like
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch dish like: {str(e)}")
            raise DatabaseError(
                detail="Failed to fetch dish like",
                extra={"original_error": str(e)}
            )


    def toggle_like(self, dish_id: int, user_id: uuid.UUID) -> bool:
        """Toggle the like status of a dish"""
        existing_like = self.get_like(dish_id, user_id)


        if existing_like:
            # If the user already liked the dish, remove the like
            self.db.delete(existing_like)
            self.db.commit()
            return False
        else:
            # If the user has not liked the dish yet, add a new like
            new_like = DishLikeTable(dish_id=dish_id, user_id=user_id)
            self.db.add(new_like)
            self.db.commit()
            return True

        

        


    def get_dates(self, dish_id: int):
        """Get all dates, canteen IDs, and canteen information for a specific dish."""
        try:
            stmt = (
                select(
                    MenuDishAssociation.menu_day_date,
                    MenuDayTable.canteen_id,
                    CanteenTable
                )
                .join(
                    MenuDayTable,
                    and_(
                        MenuDishAssociation.menu_day_date == MenuDayTable.date,
                        MenuDishAssociation.menu_day_canteen_id == MenuDayTable.canteen_id
                    )
                )
                .join(
                    CanteenTable,
                    MenuDayTable.canteen_id == CanteenTable.id
                )
                .where(MenuDishAssociation.dish_id == dish_id)
                .order_by(MenuDishAssociation.menu_day_date)
            )
            
            dish_dates = self.db.execute(stmt).all()
            
            if not dish_dates:
                raise NotFoundError(
                    detail="No dates found for the specified dish",
                    extra={"dish_id": dish_id}
                )
            
            return dish_dates
        
        except SQLAlchemyError as e:
            raise DatabaseError(
                detail="Failed to fetch dish dates",
                extra={"original_error": str(e)}
            )

