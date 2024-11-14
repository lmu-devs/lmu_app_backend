from datetime import date, datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey

from api.api_key import get_system_api_key_header, get_user_from_api_key_soft
from api.database import get_db
from api.models.menu_model import MenusDto
from api.models.user_model import UserTable
from api.routers.models.menu_pydantic import menu_days_to_pydantic
from api.service.menu_service import get_menu_days_from_db
from data_fetcher.main import fetch_data_current_year
from data_fetcher.service.menu_service import update_menu_database

router = APIRouter()

@router.get("/menus", response_model=MenusDto)
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
    current_user: UserTable = Depends(get_user_from_api_key_soft),
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
    
    menu_days = get_menu_days_from_db(
        db, 
        canteen_id, 
        date_from,
        date_to,
        current_user, 
        only_liked_canteens
    )
    
    return menu_days_to_pydantic(menu_days, user_id)

@router.put("/menus/update-all")
async def update_all_menus(api_key: APIKey = Depends(get_system_api_key_header)):
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
    api_key: APIKey = Depends(get_system_api_key_header)
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


    

    
    




