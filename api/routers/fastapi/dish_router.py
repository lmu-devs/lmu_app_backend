from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.dish_model import DishDatesDto, DishTable
from api.routers.models.dish_pydantic import dish_dates_to_pydantic


router = APIRouter()


# Gets dish data
@router.get("/dishes/{dish_id}", response_model=dict)
async def get_dish(dish_id: str, Session = Depends(get_db)):
    pass


# Gets list of multiple canteens where dish is available in past and future dates
@router.get("/dish/{dish_id}/dates", response_model=DishDatesDto)
async def read_dish_dates(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(DishTable).filter(DishTable.id == dish_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish_dates_to_pydantic(db, dish_id)




