from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.core.api_key import APIKey
from shared.database import get_db
from api.models.canteen_model import CanteenTable
from api.models.user_model import UserTable
from api.pydantics.canteen_pydantic import canteen_to_pydantic
from api.schemas.canteen_scheme import Canteens
from api.services.canteen_service import CanteenService
from data_fetcher.service.canteen_service import update_canteen_database

router = APIRouter()


@router.get("/canteens", response_model=Canteens)
async def read_canteens(
    canteen_id: Optional[str] = Query(None, description="Specific canteen ID to fetch"),
    db: Session = Depends(get_db),
    current_user: Optional[UserTable] = Depends(APIKey.get_user_from_key_soft)
):
    canteen_service = CanteenService(db)
    # Fetch a specific canteen
    if canteen_id:
        canteen = canteen_service.get_canteen(canteen_id)
        likes_canteen = bool(canteen_service.get_like(canteen_id, current_user.id)) if current_user else None
        return Canteens([canteen_to_pydantic(canteen, likes_canteen)])
    
    # Fetch all canteens
    else:
        canteens = db.query(CanteenTable).all()
        if current_user:
            likes_canteens = canteen_service.get_user_liked(current_user.id, canteens)
            return Canteens([
                canteen_to_pydantic(canteen, likes_canteens.get(canteen.id, False))
                for canteen in canteens
            ])
        else:
            return Canteens([canteen_to_pydantic(canteen) for canteen in canteens])




@router.put("/canteens/update", response_model=dict)
async def trigger_canteen_update(api_key: APIKey = Depends(APIKey.get_system_key_header)):
    return {"message": update_canteen_database()}




@router.post("/canteens/toggle-like", response_model=bool)
def toggle_like(
    canteen_id: str,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.get_user_from_key)
) -> bool:
    return CanteenService(db).toggle_like(canteen_id, current_user.id)
