from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.v1.core import APIKey
from shared.core.logging import get_food_logger
from shared.database import get_db
from shared.enums.mensa_enums import CanteenEnum
from shared.tables.user_table import UserTable

from ..pydantics.canteen_pydantic import canteen_to_pydantic
from ..schemas import Canteens
from ..services import CanteenService

router = APIRouter()
food_logger = get_food_logger(__name__)


@router.get("/canteens", response_model=Canteens)
async def get_canteens(
    canteen_id: Optional[str] = Query(None, description="Optional canteen_id to fetch", example="mensa-leopoldstr", enum=[canteen.value for canteen in CanteenEnum]),
    db: Session = Depends(get_db),
    current_user: Optional[UserTable] = Depends(APIKey.verify_user_api_key_soft)
):
    canteen_service = CanteenService(db)
    if canteen_id:
        canteen = canteen_service.get_canteen(canteen_id)
        likes_canteen = bool(canteen_service.get_like(canteen_id, current_user.id)) if current_user else None
        food_logger.info(f"Fetched canteen {canteen_id} with likes_canteen: {likes_canteen}")
        return Canteens([canteen_to_pydantic(canteen, likes_canteen)])
    

    canteens = canteen_service.get_all_active_canteens()
    if current_user:
        likes_canteens = canteen_service.get_user_liked(current_user.id, canteens)
        food_logger.info(f"Fetched {len(canteens)} active canteens with likes_canteens: {likes_canteens}")
        return Canteens([
            canteen_to_pydantic(canteen, likes_canteens.get(canteen.id, False))
            for canteen in canteens
        ])

    food_logger.info(f"Fetched {len(canteens)} active canteens")
    return Canteens([canteen_to_pydantic(canteen) for canteen in canteens])




@router.post("/canteens/toggle-like", response_model=bool, description="Authenticated user can toggle like for a canteen. Returns True if the canteen was liked, False if it was unliked.")
def toggle_like(
    canteen_id: str = Query(..., description="Canteen ID to toggle like", example="mensa-leopoldstr", enum=[canteen.value for canteen in CanteenEnum]),
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key)
) -> bool:
    canteen_service = CanteenService(db)
    result = canteen_service.toggle_like(canteen_id, current_user.id)
    food_logger.info(f"Toggled like for canteen {canteen_id} by user {current_user.id}. Result: {result}")
    return result
