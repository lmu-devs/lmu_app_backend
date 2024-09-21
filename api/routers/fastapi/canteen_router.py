from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey

from api.api_key import get_system_api_key_header, get_user_from_api_key, get_user_from_api_key_soft
from api.database import get_db
from api.models.canteen_model import CanteenTable, CanteensDto
from api.models.user_model import UserTable
from api.routers.models.canteen_pydantic import canteen_to_pydantic
from api.service.canteen_service import check_user_likes_canteen, get_canteen_from_db, get_user_liked_canteens, toggle_canteen_like
from data_fetcher.service.canteen_service import update_canteen_database



router = APIRouter()


@router.get("/canteens", response_model=CanteensDto)
async def read_canteens(
    canteen_id: Optional[str] = Query(None, description="Specific canteen ID to fetch"),
    db: Session = Depends(get_db),
    current_user: Optional[UserTable] = Depends(get_user_from_api_key_soft)
):
    # Fetch a specific canteen
    if canteen_id:
        canteen = get_canteen_from_db(canteen_id, db)
        likes_canteen = check_user_likes_canteen(canteen.id, current_user.id, db) if current_user else None
        return CanteensDto([canteen_to_pydantic(canteen, likes_canteen)])
    
    # Fetch all canteens
    else:
        canteens = db.query(CanteenTable).all()
        if current_user:
            likes_canteens = get_user_liked_canteens(current_user.id, canteens, db)
            return CanteensDto([
                canteen_to_pydantic(canteen, likes_canteens.get(canteen.id, False))
                for canteen in canteens
            ])
        else:
            return CanteensDto([canteen_to_pydantic(canteen) for canteen in canteens])




@router.put("/canteens/update", response_model=dict)
async def trigger_canteen_update(api_key: APIKey = Depends(get_system_api_key_header)):
    update_canteen_database()
    return {"message": "All canteens updated successfully"}




@router.post("/canteens/toggle-like", response_model=bool)
def toggle_like(
    canteen_id: str,
    db: Session = Depends(get_db), 
    current_user: UserTable = Depends(get_user_from_api_key)) -> bool:

    like_status = toggle_canteen_like(canteen_id, current_user.id, db)
    return like_status
