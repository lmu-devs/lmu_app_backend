from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security.api_key import APIKey

from api.api_key import get_api_key
from api.database import get_db
from api.models.menu_model import MenuWeekDto, MenuWeekTable, MenusDto
from api.routers.models.menu_pydantic import menu_week_to_pydantic
from data_fetcher.service.menu_service import update_menu_database

router = APIRouter()

@router.put("/menus/update-all", )
async def update_all_menus(api_key: APIKey = Depends(get_api_key)):
    try:
        update_menu_database()
        return {"message": "Menu items for all canteens updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating menu items: {str(e)}")

@router.put("/menus/{canteen_id}/{year}/{week}")
async def update_menu(canteen_id: str, year: int, week: str, api_key: APIKey = Depends(get_api_key)):
    try:
        update_menu_database(canteen_id=canteen_id, year=year, week=week)
        return {"message": f"Menu items for canteen {canteen_id}, year {year}, week {week} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating menu items: {str(e)}")

    

    
@router.get("/menus/all", response_model=MenusDto)
async def get_all_menus(db: Session = Depends(get_db)):
    menu_weeks = db.query(MenuWeekTable).all()
    return MenusDto(root=[menu_week_to_pydantic(menu_week) for menu_week in menu_weeks])
    
@router.get("/menus/{canteen_id}/{year}/{week}", response_model=MenuWeekDto)
async def get_menu(canteen_id: str, year: int, week: str, db: Session = Depends(get_db)):
    menu_week_obj = db.query(MenuWeekTable).filter(
        MenuWeekTable.canteen_id == canteen_id,
        MenuWeekTable.year == year,
        MenuWeekTable.week == week
    ).first()
    if menu_week_obj is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return menu_week_to_pydantic(menu_week_obj)



# @router.get("/menus/{canteen_id}/all", response_model=MenusDto)
# async def get_all_menus_for_canteen(canteen_id: str, db: Session = Depends(get_db)):
#     menu_weeks = db.query(MenuWeekTable).filter(MenuWeekTable.canteen_id == canteen_id).all()
#     return MenusDto(root=[menu_week_to_pydantic(menu_week) for menu_week in menu_weeks])



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



