from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey

from api.api_key import get_system_api_key_header, get_user_from_api_key_soft
from api.database import get_db
from api.models.dish_model import DishTable
from api.models.menu_model import MenuWeekDto
from api.models.user_model import UserTable
from api.routers.models.menu_pydantic import menu_week_to_pydantic
from api.service.dish_service import get_user_liked_dishes_dict
from api.service.menu_service import get_menu_week_from_db
from data_fetcher.main import fetch_data_current_year
from data_fetcher.service.menu_service import update_menu_database

router = APIRouter()


@router.get("/menus", response_model=MenuWeekDto)
async def get_menu(
    canteen_id: str, 
    year: int, 
    week: str, 
    db: Session = Depends(get_db),
    current_user: Optional[UserTable] = Depends(get_user_from_api_key_soft)
    ):
    
    menu_week_obj = get_menu_week_from_db(db, canteen_id, year, week)
    
    if current_user:
        dishes_table: List[DishTable] = []
        for menu_day in menu_week_obj.menu_days:
            for association in menu_day.dish_associations:
                dish = association.dish
                dishes_table.append(dish)
        
        liked_dishes = get_user_liked_dishes_dict(current_user.id, dishes_table, db)
        return menu_week_to_pydantic(menu_week_obj, liked_dishes)
    
    return menu_week_to_pydantic(menu_week_obj)



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


    

    
    




