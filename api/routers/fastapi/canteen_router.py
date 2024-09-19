import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKey

from api.api_key import get_system_api_key_header, get_user_api_key_header
from api.database import get_db
from api.models.canteen_model import CanteenTable, CanteenDto, CanteensDto
from api.routers.models.canteen_pydantic import canteen_to_pydantic
from api.service.canteen_service import toggle_canteen_like
from data_fetcher.service.canteen_service import update_canteen_database



router = APIRouter()





@router.get("/canteens/", response_model=CanteensDto)
async def read_canteens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    canteens = db.query(CanteenTable).offset(skip).limit(limit).all()
    return CanteensDto([canteen_to_pydantic(canteen) for canteen in canteens])

@router.get("/canteens/{canteen_id}", response_model=CanteenDto)
async def read_canteen(canteen_id: str, db: Session = Depends(get_db)):
    canteen = db.query(CanteenTable).filter(CanteenTable.id == canteen_id).first()
    if canteen is None:
        raise HTTPException(status_code=404, detail="canteen not found")
    return canteen_to_pydantic(canteen)



@router.put("/canteens/update", response_model=dict)
async def trigger_canteen_update(api_key: APIKey = Depends(get_system_api_key_header)):
    print("Triggering canteen update process...")
    try:
        update_canteen_database()
        return {"message": "canteen update process has been triggered"}
    except Exception as e:
        print(f"Error triggering canteen update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.post("/canteens/toggle-like", response_model=bool)
def toggle_like(canteen_id: str, user_id: uuid.UUID, db: Session = Depends(get_db), api_key: str = Depends(get_user_api_key_header)):
    try:
        result = toggle_canteen_like(canteen_id, user_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))