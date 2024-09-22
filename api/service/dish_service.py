from typing import List, Optional
import uuid
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, noload
from sqlalchemy.exc import SQLAlchemyError

from api.models.canteen_model import CanteenTable
from api.models.dish_model import DishTable, DishLikeTable
from api.models.menu_model import MenuDayTable, MenuDishAssociation


def get_dishes_from_db(
    db: Session, 
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
        dishes =  db.execute(stmt).scalars().all()

        if not dishes:
            raise HTTPException(status_code=404, detail=f"Dish with id {dish_id} not found")

        return dishes

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e
    


def get_dish_like_from_db(dish_id: int, user_id: uuid.UUID, db: Session) -> DishLikeTable:
    """Get the like status of a dish by a user"""
    try:
        stmt = (
            select(DishLikeTable)
            .where(
                DishLikeTable.dish_id == dish_id,
                DishLikeTable.user_id == user_id
            )
        )
        
        result = db.execute(stmt)
        dish_like = result.scalar_one_or_none()
        
        return dish_like
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e


def toggle_dish_like(dish_id: int, user_id: uuid.UUID, db: Session) -> bool:
    """Toggle the like status of a dish"""
    existing_like = get_dish_like_from_db(dish_id, user_id, db)

    if existing_like:
        # If the user already liked the dish, remove the like
        db.delete(existing_like)
        db.commit()
        return False
    else:
        # If the user has not liked the dish yet, add a new like
        try:
            new_like = DishLikeTable(dish_id=dish_id, user_id=user_id)
            db.add(new_like)
            db.commit()
            return True
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred") from e
    

    


def get_dish_dates_from_db(db: Session, dish_id: int):
    """Get all dates, canteen IDs, and canteen information for a specific dish."""
    try:
        stmt = (
            select(
                MenuDishAssociation.menu_day_date,
                MenuDayTable.menu_week_canteen_id,
                CanteenTable
            )
            .join(MenuDayTable, MenuDishAssociation.menu_day_date == MenuDayTable.date)
            .join(CanteenTable, MenuDayTable.menu_week_canteen_id == CanteenTable.id)
            .where(MenuDishAssociation.dish_id == dish_id)
            .order_by(MenuDishAssociation.menu_day_date)
        )
        
        dish_dates = db.execute(stmt).all()
        
        if not dish_dates:
            raise HTTPException(status_code=404, detail=f"No dates found for dish with id {dish_id}")
        
        return dish_dates
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e
