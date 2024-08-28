from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.canteen_model import CanteenTable, CanteenDto, CanteensDto
from app.routers.models.canteen_pydantic import canteen_to_pydantic
from app.services.canteen_service import update_canteen_database

router = APIRouter()

@router.get("/canteen/trigger-update", response_model=dict)
async def trigger_canteen_update(background_tasks: BackgroundTasks):
    print("Triggering canteen update process...")
    try:
        update_canteen_database()
        return {"message": "canteen update process has been triggered"}
    except Exception as e:
        print(f"Error triggering canteen update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/canteens/", response_model=CanteensDto)
async def read_canteens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    canteens = db.query(CanteenTable).offset(skip).limit(limit).all()
    return CanteensDto([canteen_to_pydantic(canteen) for canteen in canteens])

@router.get("/canteen/{canteen_id}", response_model=CanteenDto)
async def read_canteen(canteen_id: str, db: Session = Depends(get_db)):
    canteen = db.query(CanteenTable).filter(CanteenTable.canteen_id == canteen_id).first()
    if canteen is None:
        raise HTTPException(status_code=404, detail="canteen not found")
    return canteen_to_pydantic(canteen)