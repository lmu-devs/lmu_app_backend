from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models.user_model import UserTable
from api.core.api_key import APIKey
from api.schemas.menu_scheme import Menus
from api.pydantics.menu_pydantic import menu_days_to_pydantic
from api.services.menu_service import MenuService
from shared.core.logging import get_menu_logger

router = APIRouter()
menu_logger = get_menu_logger(__name__)

@router.get("/menus", response_model=Menus, description="Get all menus or a specific canteen by ID. Authenticated users can also get liked dishes.")
async def get_menu(
    date_from: Optional[date] = Query(
        default=datetime.now().date(),
        description="Start date for menu search. Defaults to today",
        example=datetime.now().date()
        
    ),
    days_amount: int = Query(
        default=14,
        description="Number of days to fetch from start date",
        ge=1,
        le=31
    ),
    canteen_id: str = Query(
        default=None,
        description="Filter by canteen_id, if not provided, all canteens will be fetched",
        example="mensa-leopoldstr"
    ),
    current_user: UserTable = Depends(APIKey.get_user_from_key_soft),
    only_liked_canteens: bool = Query(
        default=False,
        description="Filter menus by liked canteens"
    ),
    db: Session = Depends(get_db)
):
    
    date_to = date_from + timedelta(days=days_amount)
    user_id = current_user.id if current_user else None
    
    
    menu_service = MenuService(db)
    menu_days = menu_service.get_days(
        canteen_id, 
        date_from,
        date_to,
        current_user, 
        only_liked_canteens
    )
    menu_logger.info(f"Fetched menu days for canteen {canteen_id} from {date_from} to {date_to} with user_id: {user_id} and only_liked_canteens: {only_liked_canteens}")
    
    return menu_days_to_pydantic(menu_days, user_id)


    

    
    




