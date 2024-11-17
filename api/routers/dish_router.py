from typing import Annotated, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from shared.core.language import Language, get_language
from shared.database import get_db
from shared.models.canteen_model import CanteenTable
from shared.models.user_model import UserTable
from api.core.api_key import APIKey
from api.schemas.dish_scheme import DishDates, Dishes
from api.pydantics.dish_pydantic import (dish_dates_to_pydantic, dish_to_pydantic)
from api.services.canteen_service import CanteenService
from api.services.dish_service import DishService
from shared.core.logging import get_dish_logger

router = APIRouter()
dish_logger = get_dish_logger(__name__)

# Gets dish data
@router.get("/dishes", response_model=Dishes, description="Get all dishes or a specific dish by ID. Authenticated users can also get liked dishes.")
async def get_dish(
    id: Annotated[int, Query(
        description="Specific dish ID to fetch",
        gt=0,
        example=11,
        title="Dish ID"
    )] = None,
    only_liked_dishes: bool = Query(None, description="Filter dishes by liked status"),
    current_user: UserTable = Depends(APIKey.get_user_from_key_soft),
    db: Session = Depends(get_db),
    language: Language = Depends(get_language)
    ):
    
    user_id = current_user.id if current_user else None
    dishes = DishService(db).get_dishes(id, user_id, only_liked_dishes)
    dish_logger.info(f"Fetched dishes {id} with user_id: {user_id} and only_liked_dishes: {only_liked_dishes}")
    
    return Dishes(dishes=[dish_to_pydantic(dish, user_id) for dish in dishes])



# Gets list of multiple canteens where dish is available in past and future dates
@router.get("/dishes/dates", response_model=DishDates, description="Get all canteens where a dish is available in past and future dates")
async def read_dish_dates(
    dish_id: Annotated[int, Query(
        ..., 
        description="Specific dish ID find dates for",
        gt=0,
        example=11,
        title="Dish ID"
    )],
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.get_user_from_key_soft)
    ):
    
    dish_dates = DishService(db).get_dates(dish_id)
    
    user_likes_canteen = None
    
    if current_user:
        canteens: List[CanteenTable] = [row[2] for row in dish_dates]
        user_likes_canteen = CanteenService(db).get_user_liked(current_user.id, canteens)
    
    dish_logger.info(f"Fetched dish dates {dish_id} with user_id: {current_user.id} and user_likes_canteen: {user_likes_canteen}")
    
    return dish_dates_to_pydantic(dish_dates, user_likes_canteen)



@router.post("/dishes/toggle-like", response_model=bool, description="Authenticated user can toggle like for a dish. Returns True if the dish was liked, False if it was unliked.")
def toggle_like(
    dish_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserTable = Depends(APIKey.get_user_from_key)
    ):

    like_status = DishService(db).toggle_like(dish_id, current_user.id)
    dish_logger.info(f"Toggled like for dish {dish_id} by user {current_user.id}. Result: {like_status}")
    return like_status

    







