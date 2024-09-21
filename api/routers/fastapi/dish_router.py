from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.models.canteen_model import CanteenTable
from api.models.dish_model import DishDatesDto, DishesDto
from api.models.user_model import UserTable
from api.api_key import get_user_from_api_key_soft, get_user_from_api_key
from api.database import get_db
from api.routers.models.dish_pydantic import dish_dates_to_pydantic, dish_to_pydantic
from api.service.canteen_service import get_user_liked_canteens
from api.service.dish_service import check_user_likes_dish, get_all_dishes_from_db, get_dish_dates_from_db, get_dish_from_db, get_liked_dishes_from_db, get_user_liked_dishes_dict, toggle_dish_like


router = APIRouter()


# Gets dish data
@router.get("/dishes", response_model=DishesDto)
async def get_dish(
    dish_id: Annotated[Optional[int], Query(
        description="Specific dish ID to fetch",
        gt=0,
        example=11,
        title="Dish ID"
    )] = None,
    only_liked_dishes: Optional[bool] = Query(None, description="Filter dishes by liked status"),
    current_user: Optional[UserTable] = Depends(get_user_from_api_key_soft),
    db: Session = Depends(get_db)
    ):
    
    user_liked_dishes = None
    if dish_id:
        dish = get_dish_from_db(dish_id, db)
        if current_user:
            user_liked_dishes = check_user_likes_dish(dish.id, current_user.id, db)
            
        return DishesDto(dishes=[dish_to_pydantic(dish, user_liked_dishes)])

    else:
        if only_liked_dishes and current_user:
            liked_dishes = get_liked_dishes_from_db(current_user.id, db)
            return DishesDto(dishes=[dish_to_pydantic(dish, True) for dish in liked_dishes])
        
        dishes = get_all_dishes_from_db(db)
        if current_user:
            user_liked_dishes = get_user_liked_dishes_dict(current_user.id, dishes, db)
            dishes_dto: DishesDto = DishesDto(dishes=[
                dish_to_pydantic(
                    dish,
                    user_likes_dish=user_liked_dishes.get(dish.id, False) if user_liked_dishes else None
                )
                for dish in dishes
            ])
            return dishes_dto

        else:
            return DishesDto(dishes=[dish_to_pydantic(dish, user_liked_dishes) for dish in dishes])



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

    







