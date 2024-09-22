from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.models.canteen_model import CanteenTable
from api.models.dish_model import DishDatesDto, DishesDto
from api.models.user_model import UserTable
from api.api_key import get_user_from_api_key_soft, get_user_from_api_key
from api.database import get_db
from api.routers.models.dish_pydantic import dish_dates_to_pydantic, dish_to_pydantic
from api.service.canteen_service import get_user_liked_canteens
from api.service.dish_service import get_dish_dates_from_db, get_dishes_from_db, toggle_dish_like


router = APIRouter()


# Gets dish data
@router.get("/dishes", response_model=DishesDto)
async def get_dish(
    dish_id: Annotated[int, Query(
        description="Specific dish ID to fetch",
        gt=0,
        example=11,
        title="Dish ID"
    )] = None,
    only_liked_dishes: bool = Query(None, description="Filter dishes by liked status"),
    current_user: UserTable = Depends(get_user_from_api_key_soft),
    db: Session = Depends(get_db)
    ):
    
    user_id = current_user.id if current_user else None
    dishes = get_dishes_from_db(db, dish_id, user_id, only_liked_dishes)
    
    return DishesDto(dishes=[dish_to_pydantic(dish, user_id) for dish in dishes])



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
    current_user: UserTable = Depends(get_user_from_api_key_soft)
    ):
    
    dish_dates = get_dish_dates_from_db(db, dish_id)
    
    user_likes_canteen = None
    
    if current_user:
        canteens: List[CanteenTable] = [row[2] for row in dish_dates]
        user_likes_canteen = get_user_liked_canteens(current_user.id, canteens, db)
    
    return dish_dates_to_pydantic(dish_dates, user_likes_canteen)





@router.post("/dishes/toggle-like", response_model=bool)
def toggle_like(
    dish_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserTable = Depends(get_user_from_api_key)
    ):

    like_status = toggle_dish_like(dish_id, current_user.id, db)
    return like_status

    







