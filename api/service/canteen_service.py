from typing import Dict, List
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from api.models.canteen_model import CanteenLikeTable, CanteenTable
import uuid

from api.models.user_model import UserTable

# Check if the canteen exists
def get_canteen_from_db(canteen_id: str, db: Session) -> CanteenTable:
    """Retrieve a canteen from the database by its ID."""
    try:
        canteen = db.query(CanteenTable).filter(CanteenTable.id == canteen_id).first()
        if canteen is None:
            raise HTTPException(status_code=404, detail=f"Canteen with id {canteen_id} not found")
        return canteen
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e




def get_canteen_like_from_db(canteen_id: int, user_id: str, db: Session) -> CanteenLikeTable:
    """Get the like status of a canteen by a user"""
    try:
        canteen_like = db.query(CanteenLikeTable).filter(
            CanteenLikeTable.canteen_id == canteen_id,
            CanteenLikeTable.user_id == user_id
        ).one()
        return canteen_like
    
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred") from e


def check_user_likes_canteen(canteen_id: int, user_id: str, db: Session) -> bool:  
    """Check if a user likes a canteen"""
    return bool(get_canteen_like_from_db(canteen_id, user_id, db))


def toggle_canteen_like(canteen_id: str, user_id: uuid.UUID, db: Session) -> bool:
    """Toggle the like status of a canteen by a user"""
    existing_like = get_canteen_like_from_db(canteen_id, user_id, db)

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
    


def get_user_liked_canteens(user_id: uuid.UUID, canteens: List[CanteenTable], db: Session) -> Dict[str, bool]:
    canteen_ids = [canteen.id for canteen in canteens]
    liked_canteens = db.query(CanteenLikeTable.canteen_id).filter(
        and_(
            CanteenLikeTable.user_id == user_id,
            CanteenLikeTable.canteen_id.in_(canteen_ids)
        )
    ).all()
    
    liked_canteen_ids = {canteen_id for (canteen_id,) in liked_canteens}
    return {canteen.id: canteen.id in liked_canteen_ids for canteen in canteens}