from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.models.canteen_model import CanteenTable
from api.models.dish_model import DishDatesDto, DishDto
from api.models.user_model import UserTable
from api.api_key import get_user_from_api_key_soft, get_user_from_api_key
from api.database import get_db
from api.routers.models.dish_pydantic import dish_dates_to_pydantic, dish_to_pydantic
from api.service.canteen_service import check_user_likes_canteen, get_user_liked_canteens
from api.service.dish_service import check_user_likes_dish, get_dish_dates_from_db, get_dish_from_db, toggle_dish_like


router = APIRouter()


# Gets dish data
@router.get("/dishes", response_model=DishDto)
async def get_dish(
    dish_id: Annotated[int, Query(
        ..., 
        description="Specific dish ID to fetch",
        gt=0,
        example=11,
        title="Dish ID"
    )],
    db: Session = Depends(get_db), 
    current_user: Optional[UserTable] = Depends(get_user_from_api_key_soft)
    ):

    dish = get_dish_from_db(dish_id, db)
    
    user_likes_dish = None
    if current_user:
        user_likes_dish = check_user_likes_dish(current_user, dish, db)

    return dish_to_pydantic(dish, user_likes_dish)


# Gets list of multiple canteens where dish is available in past and future dates
@router.get("/dishes/dates", response_model=DishDatesDto)
async def read_dish_dates(
    dish_id: Annotated[int, Query(
        ..., 
        description="Specific dish ID find dates for",
        gt=0,
        example=11,
        title="Dish ID"
    )],
    db: Session = Depends(get_db),
    current_user: Optional[UserTable] = Depends(get_user_from_api_key_soft)
    ):
    
    dish = get_dish_from_db(dish_id, db)
    result = get_dish_dates_from_db(db, dish.id)
    user_likes_canteen = None
    
    if current_user:
        canteens: List[CanteenTable] = [row[2] for row in result]
        user_likes_canteen = get_user_liked_canteens(current_user, canteens, db)
    
    return dish_dates_to_pydantic(result, user_likes_canteen)



@router.post("/dishes/toggle-like", response_model=bool)
def toggle_like(
    dish_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserTable = Depends(get_user_from_api_key)
    ):
    try:
        result = toggle_dish_like(dish_id, current_user.id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






