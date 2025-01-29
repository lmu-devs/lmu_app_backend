from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.logging import get_food_logger
from shared.src.core.database import get_async_db
from ..models.home_model import Home
from ..services.home_service import HomeService

router = APIRouter()
logger = get_food_logger(__name__)

@router.get("/home", response_model=Home, description="Get home screen data")
async def get_home(
    db: AsyncSession = Depends(get_async_db)
):
    home_service = HomeService(db)
    return await home_service.get_home_data()