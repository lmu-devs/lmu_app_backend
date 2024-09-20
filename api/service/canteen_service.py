from typing import Dict, List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from api.models.canteen_model import CanteenLikeTable, CanteenTable
import uuid

from api.models.user_model import UserTable
from api.service.user_service import get_user_from_db

# Check if the canteen exists
def get_canteen_from_db(canteen_id: str, db: Session) -> CanteenTable | None:
    canteen = db.query(CanteenTable).filter(CanteenTable.id == canteen_id).first()
    if not canteen:
        raise Exception("Canteen not found")
    return canteen



def toggle_canteen_like(canteen_id: str, user_id: uuid.UUID, db: Session) -> bool:

    # Check if the user & canteen exists
    canteen = get_canteen_from_db(canteen_id, db)
    user = get_user_from_db(user_id, db)

    # Check if the user already liked the canteen
    existing_like = db.query(CanteenLikeTable).filter(
        CanteenLikeTable.canteen_id == canteen_id,
        CanteenLikeTable.user_id == user_id
    ).first()

    if existing_like:
        # If the user already liked the canteen, remove the like
        db.delete(existing_like)
        db.commit()
        return False
    else:
        # If the user has not liked the canteen yet, add a new like
        new_like = CanteenLikeTable(canteen_id=canteen_id, user_id=user_id)
        db.add(new_like)
        db.commit()
        return True
    
    
def check_user_likes_canteen(user: UserTable, canteen: CanteenTable, db: Session) -> bool:
    
    existing_like = db.query(CanteenLikeTable).filter(
        CanteenLikeTable.canteen_id == canteen.id,
        CanteenLikeTable.user_id == user.id
    ).first()
    
    if existing_like:
        return True
    else:
        return False


def get_user_liked_canteens(user: UserTable, canteens: List[CanteenTable], db: Session) -> Dict[str, bool]:
    canteen_ids = [canteen.id for canteen in canteens]
    liked_canteens = db.query(CanteenLikeTable.canteen_id).filter(
        and_(
            CanteenLikeTable.user_id == user.id,
            CanteenLikeTable.canteen_id.in_(canteen_ids)
        )
    ).all()
    
    liked_canteen_ids = {canteen_id for (canteen_id,) in liked_canteens}
    return {canteen.id: canteen.id in liked_canteen_ids for canteen in canteens}