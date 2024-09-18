import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.api_key import get_api_key
from api.database import get_db
from api.models.dish_model import DishDatesDto, DishDto, DishTable
from api.routers.models.dish_pydantic import dish_dates_to_pydantic, dish_to_pydantic
from api.service.dish_service import toggle_dish_like


router = APIRouter()


# Gets dish data
@router.get("/dishes/{dish_id}", response_model=DishDto)
async def get_dish(dish_id: str, db: Session = Depends(get_db)):
    dish = db.query(DishTable).filter(DishTable.id == dish_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish_to_pydantic(db, dish_id)


# Gets list of multiple canteens where dish is available in past and future dates
@router.get("/dishes/{dish_id}/dates", response_model=DishDatesDto)
async def read_dish_dates(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(DishTable).filter(DishTable.id == dish_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish_dates_to_pydantic(db, dish_id)


@router.post("/dishes/toggle-like", response_model=bool)
def toggle_like(dish_id: int, user_id: uuid.UUID, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    try:
        result = toggle_dish_like(dish_id, user_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






