from uuid import UUID
from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.logging import get_food_logger
from shared.src.core.database import get_db, get_async_db
from shared.src.enums import LanguageEnum
from shared.src.tables import CanteenTable, UserTable

from ...core import APIKey
from ...core.language import get_language

from ..pydantics.dish_pydantic import dish_dates_to_pydantic, dish_to_pydantic
from ..schemas import DishDates, Dishes
from ..services import CanteenService, DishService

router = APIRouter()
food_logger = get_food_logger(__name__)

# Gets dish data
@router.get("/dishes", response_model=Dishes, description="Get all dishes or a specific dish by ID. Authenticated users can also get liked dishes.")
async def get_dish(
    id: Annotated[UUID, Query(
        description="Specific dish ID to fetch",
        example="0d557344-d228-5032-8b0c-bca7cefc0934",
        title="Dish ID"
    )] = None,
    only_liked_dishes: bool = Query(None, description="Filter dishes by liked status"),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    db: Session = Depends(get_db),
    language: LanguageEnum = Depends(get_language)
    ):
    
    user_id = current_user.id if current_user else None
    dishes = DishService(db).get_dishes(id, user_id, only_liked_dishes, language)
    food_logger.info(f"Fetched dishes {id} with user_id: {user_id} and only_liked_dishes: {only_liked_dishes} with language: {language}")
    
    return Dishes(dishes=[dish_to_pydantic(dish, user_id) for dish in dishes])



# Gets list of multiple canteens where dish is available in past and future dates
@router.get("/dishes/dates", response_model=DishDates, description="Get all canteens where a dish is available in past and future dates")
async def read_dish_dates(
    dish_id: Annotated[UUID, Query(
        ..., 
        description="Specific dish ID find dates for",
        example="0d557344-d228-5032-8b0c-bca7cefc0934",
        title="Dish ID"
    )],
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft)
    ):
    
    dish_dates = DishService(db).get_dates(dish_id)
    
    user_likes_canteen = None
    
    if current_user:
        canteens: List[CanteenTable] = [row[2] for row in dish_dates]
        user_likes_canteen = CanteenService(db).get_user_liked(current_user.id, canteens)
    
    food_logger.info(f"Fetched dish dates {dish_id} with user_id: {current_user.id if current_user else None} and user_likes_canteen: {user_likes_canteen}")
    
    return dish_dates_to_pydantic(dish_dates, user_likes_canteen)



@router.post("/dishes/toggle-like", response_model=bool, description="Authenticated user can toggle like for a dish. Returns True if the dish was liked, False if it was unliked.")
async def toggle_like(
    dish_id: UUID, 
    db: AsyncSession = Depends(get_async_db), 
    current_user: UserTable = Depends(APIKey.verify_user_api_key)
    ):

    like_status = await DishService(db).toggle_like(dish_id, current_user.id)
    food_logger.info(f"Toggled like for dish {dish_id} by user {current_user.id}. Result: {like_status}")
    return like_status

    







