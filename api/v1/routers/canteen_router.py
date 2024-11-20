from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.enums.mensa_enums import CanteenID
from shared.models.canteen_model import CanteenTable
from shared.models.user_model import UserTable
from shared.core.logging import get_canteen_logger
from api.v1.core.api_key import APIKey
from api.v1.pydantics.canteen_pydantic import canteen_to_pydantic
from api.v1.schemas.canteen_scheme import Canteens
from api.v1.services.canteen_service import CanteenService

router = APIRouter()
canteen_logger = get_canteen_logger(__name__)


@router.get("/canteens", response_model=Canteens, description="Get all canteens or a specific canteen by ID. Authenticated users can also get liked canteens.", )
async def get_canteens(
    canteen_id: Optional[str] = Query(None, description="Optional canteen_id to fetch", example="mensa-leopoldstr", enum=[canteen.value for canteen in CanteenID]),
    db: Session = Depends(get_db),
    current_user: Optional[UserTable] = Depends(APIKey.get_user_from_key_soft)
):
    canteen_service = CanteenService(db)
    # Fetch a specific canteen
    if canteen_id:
        canteen = canteen_service.get_canteen(canteen_id)
        likes_canteen = bool(canteen_service.get_like(canteen_id, current_user.id)) if current_user else None
        canteen_logger.info(f"Fetched canteen {canteen_id} with likes_canteen: {likes_canteen}")
        return Canteens([canteen_to_pydantic(canteen, likes_canteen)])
    
    # Fetch all canteens
    canteens = db.query(CanteenTable).all()
    if current_user:
        likes_canteens = canteen_service.get_user_liked(current_user.id, canteens)
        canteen_logger.info(f"Fetched {len(canteens)} canteens with likes_canteens: {likes_canteens}")
        return Canteens([
            canteen_to_pydantic(canteen, likes_canteens.get(canteen.id, False))
            for canteen in canteens
        ])

    canteen_logger.info(f"Fetched {len(canteens)} canteens")
    return Canteens([canteen_to_pydantic(canteen) for canteen in canteens])




@router.post("/canteens/toggle-like", response_model=bool, description="Authenticated user can toggle like for a canteen. Returns True if the canteen was liked, False if it was unliked.")
def toggle_like(
    canteen_id: str = Query(..., description="Canteen ID to toggle like", example="mensa-leopoldstr", enum=[canteen.value for canteen in CanteenID]),
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.get_user_from_key)
) -> bool:
    canteen_service = CanteenService(db)
    result = canteen_service.toggle_like(canteen_id, current_user.id)
    canteen_logger.info(f"Toggled like for canteen {canteen_id} by user {current_user.id}. Result: {result}")
    return result
