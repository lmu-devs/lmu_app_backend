from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey

from api.api_key import get_system_api_key_header, get_user_from_api_key_soft
from api.database import get_db
from api.models.dish_model import DishTable
from api.models.menu_model import MenusDto
from api.models.user_model import UserTable
from api.routers.models.menu_pydantic import menu_week_to_pydantic
from api.service.menu_service import get_menu_weeks_from_db
from data_fetcher.main import fetch_data_current_year
from data_fetcher.service.menu_service import update_menu_database

router = APIRouter()


@router.get("/menus", response_model=MenusDto)
async def get_menu(
    year: int, 
    week: str, 
    canteen_id: str = Query(None, description="Filter by canteen_id, if not provided, all canteens will be fetched"), 
    current_user: UserTable = Depends(get_user_from_api_key_soft),
    only_liked_canteens: bool = Query(None, description="Filter menus by liked canteens"),
    db: Session = Depends(get_db)
    ):
    
    user_id = current_user.id if current_user else None
    menu_weeks = get_menu_weeks_from_db(db, canteen_id, year, week, current_user, only_liked_canteens)
    
    # Adjusting for 5 days a week even if there are less menu days in the week
    menu_week_adjusted = []
    
    if current_user:
        for menu_week_obj in menu_weeks:
            dishes_table: List[DishTable] = []
            for menu_day in menu_week_obj.menu_days:
                for association in menu_day.dish_associations:
                    dish = association.dish
                    dishes_table.append(dish)
    
    return MenusDto(root = [menu_week_to_pydantic(menu_week, user_id) for menu_week in menu_weeks])



@router.put("/menus/update-all")
async def update_all_menus(api_key: APIKey = Depends(get_system_api_key_header)):
    fetch_data_current_year()
    return {"message": "Menu items for current year updated successfully"}



@router.put("/menus")
async def update_menu(
    canteen_id: str, 
    year: int, 
    week: str, 
    api_key: APIKey = Depends(get_system_api_key_header)):

    update_menu_database(canteen_id=canteen_id, year=year, week=week)
    return {"message": f"Menu items for canteen {canteen_id}, year {year}, week {week} updated successfully"}


    

    
    




