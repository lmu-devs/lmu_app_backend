from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security.api_key import APIKey

from api.api_key import get_system_api_key_header, get_user_from_api_key_soft
from api.database import get_db
from api.models.dish_model import DishTable
from api.models.menu_model import MenuDayTable, MenuDishAssociation, MenuWeekDto, MenuWeekTable, MenusDto
from api.models.user_model import UserTable
from api.routers.models.menu_pydantic import menu_week_to_pydantic
from api.service.dish_service import get_user_liked_dishes
from data_fetcher.main import fetch_data_current_year
from data_fetcher.service.menu_service import update_menu_database
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.put("/menus/update-all", )
async def update_all_menus(api_key: APIKey = Depends(get_system_api_key_header)):
    try:
        fetch_data_current_year()
        return {"message": "Menu items for all canteens updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating menu items: {str(e)}")

@router.put("/menus/{canteen_id}/{year}/{week}")
async def update_menu(canteen_id: str, year: int, week: str, api_key: APIKey = Depends(get_system_api_key_header)):
    try:
        update_menu_database(canteen_id=canteen_id, year=year, week=week)
        return {"message": f"Menu items for canteen {canteen_id}, year {year}, week {week} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating menu items: {str(e)}")

    

    
# @router.get("/menus/all", response_model=MenusDto)
# async def get_all_menus(db: Session = Depends(get_db)):
#     menu_weeks = db.query(MenuWeekTable).all()
#     return MenusDto(root=[menu_week_to_pydantic(menu_week) for menu_week in menu_weeks])
    
@router.get("/menus/{canteen_id}/{year}/{week}", response_model=MenuWeekDto)
async def get_menu(
    canteen_id: str, 
    year: int, 
    week: str, 
    db: Session = Depends(get_db),
    current_user: Optional[UserTable] = Depends(get_user_from_api_key_soft)
    ):
    
    menu_week_obj = (
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
    if menu_week_obj is None:
        raise HTTPException(status_code=404, detail="menu not found")
    
    if current_user:
        dishes_table: List[DishTable] = []
        for menu_day in menu_week_obj.menu_days:
            for association in menu_day.dish_associations:
                dish = association.dish
                dishes_table.append(dish)
        
        liked_dishes = get_user_liked_dishes(current_user, dishes_table, db)
        print(liked_dishes)
        return menu_week_to_pydantic(menu_week_obj, liked_dishes)
    
    return menu_week_to_pydantic(menu_week_obj)






@router.get("/menus/{canteen_id}/current", response_model=MenuWeekDto)
async def get_current_menu(canteen_id: str, db: Session = Depends(get_db)):
    today = datetime.now()
    week = today.strftime("%W")
    year = today.year
    return await get_menu(canteen_id, year, week, db)


@router.get("/menus/{canteen_id}/next-week", response_model=MenuWeekDto)
async def get_next_week_menu(canteen_id: str, db: Session = Depends(get_db)):
    today = datetime.now()
    next_week = today + timedelta(weeks=1)
    week = next_week.strftime("%W")
    year = next_week.year
    return await get_menu(canteen_id, year, week, db)



