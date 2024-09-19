from sqlalchemy.orm import Session
from api.models.dish_model import DishTable, DishLikeTable
from api.models.user_model import UserTable
import uuid

def toggle_dish_like(dish_id: int, user_id: uuid.UUID, db: Session) -> bool:
    # Check if the dish exists
    dish = db.query(DishTable).filter(DishTable.id == dish_id).first()
    if not dish:
        raise Exception("Dish not found")

    # Check if the user exists
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    if not user:
        raise Exception("User not found")

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
