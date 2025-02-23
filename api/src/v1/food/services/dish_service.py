import uuid
from typing import List, Optional

from sqlalchemy import Result, and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.src.core.exceptions import DatabaseError, NotFoundError
from shared.src.core.logging import get_food_logger
from shared.src.enums import LanguageEnum
from shared.src.tables import (
    CanteenTable,
    DishLikeTable,
    DishTable,
    DishTranslationTable,
    MenuDayTable,
    MenuDishAssociation,
)

from ...core.service.like_service import LikeService
from ...core.translation_utils import apply_translation_query


logger = get_food_logger(__name__)

class DishService:
    def __init__(self, db: AsyncSession):
        """Initialize the DishService with a database session."""
        self.db = db
        self.like_service = LikeService(db)
        
    async def get_dishes(
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
            # Base query with translations and eager loading
            stmt = (
                select(DishTable)
                .options(
                    selectinload(DishTable.likes),
                    selectinload(DishTable.prices),
                    selectinload(DishTable.images)
                )
            )
            
            stmt = apply_translation_query(base_query=stmt, model=DishTable, translation_model=DishTranslationTable, language=language)

            # Add filters based on parameters
            if dish_id:
                stmt = stmt.where(DishTable.id == dish_id)
                
            if user_id and only_liked:
                stmt = (
                    stmt
                    .join(DishLikeTable)
                    .where(DishLikeTable.user_id == user_id)
                )
            elif user_id:
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

            result: Result = await self.db.execute(stmt)
            dishes = result.scalars().unique().all()

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

    async def toggle_like(self, dish_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.like_service.toggle_like(DishLikeTable, dish_id, user_id)


    async def get_dates(self, dish_id: int):
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
                        MenuDishAssociation.canteen_id == MenuDayTable.canteen_id
                    )
                )
                .join(
                    CanteenTable,
                    MenuDayTable.canteen_id == CanteenTable.id
                )
                .options(
                    selectinload(CanteenTable.location),
                    selectinload(CanteenTable.opening_hours),
                    selectinload(CanteenTable.images),
                    selectinload(CanteenTable.status),
                    selectinload(CanteenTable.likes),
                    
                )
                .where(MenuDishAssociation.dish_id == dish_id)
                .order_by(MenuDishAssociation.menu_day_date)
            )
            
            result = await self.db.execute(stmt)
            dish_dates = result.all()
            
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

