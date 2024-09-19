from sqlalchemy.orm import Session
from api.models.canteen_model import CanteenLikeTable, CanteenTable
from api.models.user_model import UserTable
import uuid

def toggle_canteen_like(canteen_id: str, user_id: uuid.UUID, db: Session) -> bool:
    # Check if the canteen exists
    canteen = db.query(CanteenTable).filter(CanteenTable.id == canteen_id).first()
    if not canteen:
        raise Exception("Canteen not found")

    # Check if the user exists
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    if not user:
        raise Exception("User not found")

    # Check if the user already liked the canteen
    existing_like = db.query(CanteenLikeTable).filter(
        CanteenLikeTable.canteen_id == canteen_id,
        CanteenLikeTable.user_id == user_id
    ).first()

    if existing_like:
        # If the user already liked the canteen, remove the like
        canteen.like_count -= 1
        db.delete(existing_like)
        db.commit()
        return False
    else:
        # If the user has not liked the canteen yet, add a new like
        new_like = CanteenLikeTable(canteen_id=canteen_id, user_id=user_id)
        canteen.like_count += 1
        db.add(new_like)
        db.commit()
        return True
