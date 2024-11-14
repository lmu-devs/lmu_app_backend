import uuid

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, noload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from api.models.canteen_model import CanteenTable
from api.models.dish_model import DishTable, DishLikeTable
from api.models.menu_model import MenuDayTable, MenuDishAssociation


class DishService:
    def __init__(self, db: Session):
        """Initialize the DishService with a database session."""
        self.db = db

    def get_dishes(
        self, 
        dish_id: Optional[int] = None, 
        user_id: Optional[uuid.UUID] = None,
        only_liked: bool = False
    ) -> List[DishTable]:
        """
        Get dishes from the database.
        If dish_id is provided, return a list with only that dish.
        If user_id and only_liked are provided, return liked dishes for that user.
        Otherwise, return all dishes.
        """
        try:
            # Base query
            stmt = select(DishTable)

            if user_id and only_liked:
                stmt = stmt.join(DishLikeTable).filter(DishLikeTable.user_id == user_id)
            if dish_id:
                stmt = stmt.filter(DishTable.id == dish_id).options(noload(DishTable.likes))

            # Execute the query and return the results in one step
            dishes = self.db.execute(stmt).scalars().all()

            if not dishes:
                raise HTTPException(status_code=404, detail=f"Dish with id {dish_id} not found")

            return dishes

        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Unexpected error occurred") from e
    


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
            raise HTTPException(status_code=500, detail="Database error occurred") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Unexpected error occurred") from e


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
            try:
                new_like = DishLikeTable(dish_id=dish_id, user_id=user_id)
                self.db.add(new_like)
                self.db.commit()
                return True
            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail="Database error occurred") from e
        

        


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
                raise HTTPException(
                    status_code=404, 
                    detail=f"No dates found for dish with id {dish_id}"
                )
            
            return dish_dates
        except SQLAlchemyError as e:
            print(f"Database error in get_dish_dates_from_db: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error occurred") from e
        except Exception as e:
            print(f"Unexpected error in get_dish_dates_from_db: {str(e)}")
            raise HTTPException(status_code=500, detail="Unexpected error occurred") from e
