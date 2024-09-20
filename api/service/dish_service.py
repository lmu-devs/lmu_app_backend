from typing import Dict, List
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from api.models.canteen_model import CanteenTable
from api.models.dish_model import DishTable, DishLikeTable

from api.models.menu_model import MenuDayTable, MenuDishAssociation
from api.models.user_model import UserTable

# Check if the dish exists
def get_dish_from_db(dish_id: int, db: Session) -> DishTable | None:
    try:
        dish = db.query(DishTable).filter(DishTable.id == dish_id).first()
        if dish is None:
            raise Exception("Dish not found")
        return dish
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



def toggle_dish_like(dish_id: int, user_id: str, db: Session) -> bool:
    
    # Check the dish from the database
    get_dish_from_db(dish_id, db)

    # Check if the user already liked the dish
    existing_like = db.query(DishLikeTable).filter(
        DishLikeTable.dish_id == dish_id,
        DishLikeTable.user_id == user_id
    ).first()

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
    
    
def check_user_likes_dish(user: UserTable, dish: DishTable, db: Session) -> bool:
    
    existing_like = db.query(DishLikeTable).filter(
        DishLikeTable.dish_id == dish.id,
        DishLikeTable.user_id == user.id
    ).first()
    
    if existing_like:
        return True
    else:
        return False


def get_user_liked_dishes(user: UserTable, dishes: List[DishTable], db: Session) -> Dict[str, bool]:
    dish_ids = [dish.id for dish in dishes]
    liked_dishs = db.query(DishLikeTable.dish_id).filter(
        and_(
            DishLikeTable.user_id == user.id,
            DishLikeTable.dish_id.in_(dish_ids)
        )
    ).all()
    
    liked_dish_ids = {dish_id for (dish_id,) in liked_dishs}
    return {dish.id: dish.id in liked_dish_ids for dish in dishes}


# Query to get all dates and canteens where the dish was available
def get_dish_dates_from_db(db: Session, dish_id: int):
    query = (
        db.query(
            MenuDishAssociation.menu_day_date,
            MenuDayTable.menu_week_canteen_id,
            CanteenTable
        )
        .join(MenuDayTable, MenuDishAssociation.menu_day_date == MenuDayTable.date)
        .join(CanteenTable, MenuDayTable.menu_week_canteen_id == CanteenTable.id)
        .filter(MenuDishAssociation.dish_id == dish_id)
        .order_by(MenuDishAssociation.menu_day_date)
    )
    dish_dates = query.all()
    return dish_dates