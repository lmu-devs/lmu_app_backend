from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.security.api_key import APIKey as APIKeyHeader
from sqlalchemy.orm import Session

from api.core.api_key import APIKey
from shared.database import get_db
from api.models.user_model import UserTable
from api.schemas.menu_scheme import Menus
from api.pydantics.menu_pydantic import menu_days_to_pydantic
from api.services.menu_service import MenuService
from data_fetcher.main import fetch_data_current_year
from data_fetcher.service.menu_service import update_menu_database

router = APIRouter()

@router.get("/menus", response_model=Menus)
async def get_menu(
    date_from: date = Query(
        default=None,
        description="Start date for menu search. Defaults to today",
        example="2024-11-14"
        
    ),
    days_amount: int = Query(
        default=14,
        description="Number of days to fetch from start date",
        ge=1,
        le=31
    ),
    canteen_id: str = Query(
        default=None,
        description="Filter by canteen_id, if not provided, all canteens will be fetched"
    ),
    current_user: UserTable = Depends(APIKey.get_user_from_key_soft),
    only_liked_canteens: bool = Query(
        default=False,
        description="Filter menus by liked canteens"
    ),
    db: Session = Depends(get_db)
):
    if date_from is None:
        date_from = datetime.now().date()
    
    date_to = date_from + timedelta(days=days_amount)
    user_id = current_user.id if current_user else None
    
    menu_days = MenuService(db).get_days(
        canteen_id, 
        date_from,
        date_to,
        current_user, 
        only_liked_canteens
    )
    
    return menu_days_to_pydantic(menu_days, user_id)

@router.put("/menus/update-all")
async def update_all_menus(api_key: APIKeyHeader = Depends(APIKey.get_system_key_header)):
    fetch_data_current_year()
    return {"message": "Menu items for current year updated successfully"}

@router.put("/menus")
async def update_menu(
    canteen_id: str,
    date_from: date = Query(
        default=None,
        description="Start date for menu update. Defaults to today"
    ),
    days_amount: int = Query(
        default=14,
        description="Number of days to update from start date",
        ge=1,
        le=31
    ),
    api_key: APIKeyHeader = Depends(APIKey.get_system_key_header)
):
    if date_from is None:
        date_from = datetime.now().date()
    
    date_to = date_from + timedelta(days=days_amount)
    
    update_menu_database(
        canteen_id=canteen_id,
        date_from=date_from,
        date_to=date_to
    )
    return {
        "message": f"Menu items for canteen {canteen_id} updated for {days_amount} days starting from {date_from}"
    }


    

    
    




