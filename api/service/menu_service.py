from typing import List
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.models.canteen_model import CanteenLikeTable
from api.models.menu_model import MenuDayTable, MenuDishAssociation, MenuWeekTable

from sqlalchemy.orm import joinedload

from api.models.user_model import UserTable


def get_menu_weeks_from_db(db: Session, canteen_id: str, year: int, week: str, current_user: UserTable, only_liked_canteens: bool) -> List[MenuWeekTable]:
    """Get menu weeks from the database"""
    try:
    # Base query
        query = (
            db.query(MenuWeekTable)
            .options(
                joinedload(MenuWeekTable.canteen),
                joinedload(MenuWeekTable.menu_days)
                .joinedload(MenuDayTable.dish_associations)
                .joinedload(MenuDishAssociation.dish)
            )
            .filter(
                MenuWeekTable.year == year,
                MenuWeekTable.week == week
            )
        )

        # Apply filters based on parameters
        if canteen_id:
            query = query.filter(MenuWeekTable.canteen_id == canteen_id)
        elif only_liked_canteens and current_user:
            query = query.join(
                CanteenLikeTable,
                and_(
                    CanteenLikeTable.canteen_id == MenuWeekTable.canteen_id,
                    CanteenLikeTable.user_id == current_user.id
                )
            )
            
        # Execute query
        menu_weeks = query.all()
        
        if not menu_weeks:
            raise HTTPException(status_code=404, detail="Menu week not found")
        
        return menu_weeks
    
    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except HTTPException:
        raise

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
