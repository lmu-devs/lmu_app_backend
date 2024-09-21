from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.models.menu_model import MenuDayTable, MenuDishAssociation, MenuWeekTable

from sqlalchemy.orm import joinedload


def get_menu_week_from_db(db: Session, canteen_id: str, year: int, week: str) -> MenuWeekTable:
    try:
        menu_week = (
            db.query(MenuWeekTable)
            .options(
                joinedload(MenuWeekTable.menu_days)
                .joinedload(MenuDayTable.dish_associations)
                .joinedload(MenuDishAssociation.dish)
            )
            .filter(
                MenuWeekTable.canteen_id == canteen_id,
                MenuWeekTable.year == year,
                MenuWeekTable.week == week
            ).first()
            
        )
        if menu_week is None:
            raise HTTPException(status_code=404, detail="Menu week not found")
        
        return menu_week
    
    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except HTTPException:
        raise

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
