from sqlalchemy.orm import Session
from api.models.dish_model import DishTable, DishLikeTable
import uuid

from api.models.user_model import UserTable
from api.service.user_service import get_user_from_db

# Check if the dish exists
def get_dish_from_db(dish_id: int, db: Session) -> DishTable | None:
    dish = db.query(DishTable).filter(DishTable.id == dish_id).first()
    if not dish:
        raise Exception("Dish not found")
    return dish


def toggle_dish_like(dish_id: int, user_id: uuid.UUID, db: Session) -> bool:
    
    # Get the dish and user from the database
    dish = get_dish_from_db(dish_id, db)
    user = get_user_from_db(user_id, db)

    # Check if the user already liked the dish
    existing_like = db.query(DishLikeTable).filter(
        DishLikeTable.dish_id == dish_id,
        DishLikeTable.user_id == user_id
    ).first()

    if existing_like:
        # If the user already liked the dish, remove the like
        dish.like_count -= 1
        db.delete(existing_like)
        db.commit()
        return False
    else:
        # If the user has not liked the dish yet, add a new like
        dish.like_count += 1
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
