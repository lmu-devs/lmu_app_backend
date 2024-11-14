from typing import List
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from api.models.canteen_model import CanteenLikeTable
from api.models.menu_model import MenuDayTable, MenuDishAssociation, MenuWeekTable
from api.models.user_model import UserTable


def get_menu_weeks_from_db(db: Session, canteen_id: str, year: int, week: str, current_user: UserTable, only_liked_canteens: bool) -> List[MenuWeekTable]:
    """Get menu weeks from the database"""
    try:
        # Base query
        stmt = (
            select(MenuWeekTable)
            .options(
                joinedload(MenuWeekTable.canteen),
                joinedload(MenuWeekTable.menu_days.and_(
                    MenuDayTable.date.asc()
                ))
                .joinedload(MenuDayTable.dish_associations)
                .joinedload(MenuDishAssociation.dish)
            )
            .where(
                MenuWeekTable.year == year,
                MenuWeekTable.week == week
            )
        )

        # Apply filters based on parameters
        if canteen_id:
            stmt = stmt.where(MenuWeekTable.canteen_id == canteen_id)
        elif only_liked_canteens and current_user:
            stmt = stmt.join(
                CanteenLikeTable,
                and_(
                    CanteenLikeTable.canteen_id == MenuWeekTable.canteen_id,
                    CanteenLikeTable.user_id == current_user.id
                )
            )
            
        # Execute query
        result = db.execute(stmt)
        menu_weeks = result.unique().scalars().all()
        
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
