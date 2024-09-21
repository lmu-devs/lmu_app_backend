from typing import Dict, List
import uuid
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from api.models.canteen_model import CanteenTable
from api.models.dish_model import DishTable, DishLikeTable

from api.models.menu_model import MenuDayTable, MenuDishAssociation


def get_dish_from_db(dish_id: int, db: Session) -> DishTable:
    """Get a dish from the database by its ID"""
    try:
        dish = db.query(DishTable).filter(DishTable.id == dish_id).one()
        return dish
    
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Dish with id {dish_id} not found")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e
    
    
def get_all_dishes_from_db(db: Session) -> List[DishTable]:
    """Get all dishes"""
    try:
        dishes = db.query(DishTable).all()
        return dishes
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e
    
    
def get_liked_dishes_from_db(user_id: uuid.UUID, db: Session) -> List[DishTable]:
    """Get all dishes liked by a user"""
    try:
        liked_dishes = (
            db.query(DishTable)
            .join(DishLikeTable)
            .filter(DishLikeTable.user_id == user_id)
            .all()
        )
        return liked_dishes
    except SQLAlchemyError as e:
        # Log the error here (e.g., using logging module)
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        # Log the error here (e.g., using logging module)
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e


def get_dish_like_from_db(dish_id: int, user_id: uuid.UUID, db: Session) -> DishLikeTable:
    """Get the like status of a dish by a user"""
    try:
        dish_like = db.query(DishLikeTable).filter(
            DishLikeTable.dish_id == dish_id,
            DishLikeTable.user_id == user_id
        ).one()
        return dish_like
    
    except NoResultFound:
        return None
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
        new_like = DishLikeTable(dish_id=dish_id, user_id=user_id)
        db.add(new_like)
        db.commit()
        return True
    
    
def check_user_likes_dish(dish_id: int, user_id: uuid.UUID, db: Session) -> bool:  
    """Check if a user likes a dish"""
    return bool(get_dish_like_from_db(dish_id, user_id, db))
    

def get_user_liked_dishes_dict(user_id: uuid.UUID, dishes: List[DishTable], db: Session) -> Dict[str, bool]:
    """Get a dictionary of dish IDs and their like status for a user"""
    dish_ids = [dish.id for dish in dishes]
    liked_dishs = db.query(DishLikeTable.dish_id).filter(
        and_(
            DishLikeTable.user_id == user_id,
            DishLikeTable.dish_id.in_(dish_ids)
        )
    ).all()
    
    liked_dish_ids = {dish_id for (dish_id,) in liked_dishs}
    return {dish.id: dish.id in liked_dish_ids for dish in dishes}


def get_dish_dates_from_db(db: Session, dish_id: int):
    """Get all dates, canteen IDs, and canteen information for a specific dish."""
    try:
        dish_dates = (
            db.query(
                MenuDishAssociation.menu_day_date,
                MenuDayTable.menu_week_canteen_id,
                CanteenTable
            )
            .join(MenuDayTable, MenuDishAssociation.menu_day_date == MenuDayTable.date)
            .join(CanteenTable, MenuDayTable.menu_week_canteen_id == CanteenTable.id)
            .filter(MenuDishAssociation.dish_id == dish_id)
            .order_by(MenuDishAssociation.menu_day_date)
            .all()
        )
        
        if not dish_dates:
            raise HTTPException(status_code=404, detail=f"No dates found for dish with id {dish_id}")
        
        return dish_dates
    except SQLAlchemyError as e:
        # Log the error here (e.g., using logging module)
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        # Log the error here (e.g., using logging module)
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e