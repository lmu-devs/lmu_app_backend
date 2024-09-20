from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, Security
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey

from api.api_key import get_user_from_api_key_soft, get_user_from_api_key
from api.database import get_db
from api.models.dish_model import DishDatesDto, DishDto
from api.models.user_model import UserTable
from api.routers.models.dish_pydantic import dish_dates_to_pydantic, dish_to_pydantic
from api.service.dish_service import check_user_likes_dish, get_dish_from_db, toggle_dish_like


router = APIRouter()


# Gets dish data
@router.get("/dishes/{dish_id}", response_model=DishDto)
async def get_dish(
    dish_id: str, 
    db: Session = Depends(get_db), 
    current_user: Optional[UserTable] = Depends(get_user_from_api_key_soft)
    ):

    dish = get_dish_from_db(dish_id, db)
    
    user_likes_dish = None
    if current_user:
        user_likes_dish = check_user_likes_dish(current_user, dish, db)

    return dish_to_pydantic(dish, user_likes_dish)


# Gets list of multiple canteens where dish is available in past and future dates
@router.get("/dishes/{dish_id}/dates", response_model=DishDatesDto)
async def read_dish_dates(dish_id: int, db: Session = Depends(get_db)):
    dish = get_dish_from_db(dish_id, db)
    return dish_dates_to_pydantic(db, dish)


@router.post("/dishes/toggle-like", response_model=bool)
def toggle_like(dish_id: int, db: Session = Depends(get_db), current_user: UserTable = Depends(get_user_from_api_key)):
    try:
        result = toggle_dish_like(dish_id, current_user.id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






