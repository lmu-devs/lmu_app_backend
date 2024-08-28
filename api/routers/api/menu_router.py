from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from api.database import get_db
from api.models.menu_model import MenuWeekDto, MenuWeekTable, MenusDto
from api.routers.models.menu_pydantic import menu_week_to_pydantic
from data_fetcher.service.menu_service import update_menu_database

router = APIRouter()

@router.get("/menu/update-all", )
async def update_all_menus():
    try:
        update_menu_database()
        return {"message": "Menu items for all canteens updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating menu items: {str(e)}")

@router.get("/menu/update")
async def update_menu(
    canteen: Optional[str] = Query(None, description="Canteen ID"),
    year: Optional[int] = Query(None, description="Year of the menu"),
    week: Optional[str] = Query(None, description="Week number of the menu")):
    try:
        assert canteen is not None, "Canteen ID is required"
        assert year is not None, "Year is required"
        assert week is not None, "Week number is required"
        update_menu_database(canteen_id=canteen, year=year, week=week)
        return {"message": f"Menu items for canteen {canteen}, year {year}, week {week} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating menu items: {str(e)}")
    

    
@router.get("/menu/all", response_model=MenusDto)
async def get_all_menus(db: Session = Depends(get_db)):
    menu_weeks = db.query(MenuWeekTable).all()
    return MenusDto(root=[menu_week_to_pydantic(menu_week) for menu_week in menu_weeks])
    
@router.get("/menu/{canteen_id}/{year}/{week}", response_model=MenuWeekDto)
async def get_menu(canteen_id: str, year: int, week: str, db: Session = Depends(get_db)):
    menu_week_obj = db.query(MenuWeekTable).filter(
        MenuWeekTable.canteen_id == canteen_id,
        MenuWeekTable.year == year,
        MenuWeekTable.week == week
    ).first()
    if menu_week_obj is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return menu_week_to_pydantic(menu_week_obj)



@router.get("/menu/{canteen_id}/all", response_model=MenusDto)
async def get_all_menus_for_canteen(canteen_id: str, db: Session = Depends(get_db)):
    menu_weeks = db.query(MenuWeekTable).filter(MenuWeekTable.canteen_id == canteen_id).all()
    return MenusDto(root=[menu_week_to_pydantic(menu_week) for menu_week in menu_weeks])



@router.get("/menu/{canteen_id}/current", response_model=MenuWeekDto)
async def get_current_menu(canteen_id: str, db: Session = Depends(get_db)):
    today = datetime.now()
    week = today.strftime("%W")
    year = today.year
    return await get_menu(canteen_id, year, week, db)


@router.get("/menu/{canteen_id}/next-week", response_model=MenuWeekDto)
async def get_next_week_menu(canteen_id: str, db: Session = Depends(get_db)):
    today = datetime.now()
    next_week = today + timedelta(weeks=1)
    week = next_week.strftime("%W")
    year = next_week.year
    return await get_menu(canteen_id, year, week, db)



