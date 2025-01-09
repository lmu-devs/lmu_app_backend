from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.src.core.logging import get_food_logger
from shared.src.core.database import get_db
from ..schemas.home_scheme import Home
from ..services.home_service import HomeService

router = APIRouter()
logger = get_food_logger(__name__)

@router.get("/home", response_model=Home, description="Get home screen data")
async def get_home(
    db: Session = Depends(get_db)
):
    home_service = HomeService(db)
    return home_service.get_home_data().model_dump()