import asyncio

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.core.logging import get_food_logger
from shared.src.enums import CanteenEnum
from shared.src.tables import UserTable

from ...core import APIKey
from ..pydantics.canteen_pydantic import canteen_to_pydantic
from ..models import Canteens
from ..services import CanteenService


router = APIRouter()
food_logger = get_food_logger(__name__)


@router.get("/canteens", response_model=Canteens)
async def get_canteens(
    canteen_id: Optional[str] = Query(
        None, 
        description="Optional canteen_id to fetch", 
        example="mensa-leopoldstr", 
        enum=CanteenEnum.get_active_canteens_values()),
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[UserTable] = Depends(APIKey.verify_user_api_key_soft)
):
    service = CanteenService(db)
    
    if current_user:
        canteens, likes = await asyncio.gather(
            service.get_canteens(canteen_id),
            service.get_user_liked(current_user.id)
        )
        food_logger.info(f"Fetched {'canteen' if canteen_id else 'all active canteens'}")
        return Canteens([
            canteen_to_pydantic(canteen, likes.get(canteen.id, False))
            for canteen in canteens
        ])

    canteens = await service.get_canteens(canteen_id)
    food_logger.info(f"Fetched {'canteen' if canteen_id else 'all active canteens'}")
    return Canteens([canteen_to_pydantic(canteen) for canteen in canteens])




@router.post("/canteens/toggle-like", response_model=bool, description="Authenticated user can toggle like for a canteen. Returns True if the canteen was liked, False if it was unliked.")
async def toggle_like(
    canteen_id: str = Query(..., description="Canteen ID to toggle like", example="mensa-leopoldstr", enum=[canteen.value for canteen in CanteenEnum]),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key)
) -> bool:
    canteen_service = CanteenService(db)
    result = await canteen_service.toggle_like(canteen_id, current_user.id)
    food_logger.info(f"Toggled like for canteen {canteen_id} by user {current_user.id}. Result: {result}")
    return result