from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.enums import LanguageEnum

from ..models.sport_model import SportType, SportTypes
from ..services.sport_service import SportService


router = APIRouter()
logger = get_places_logger(__name__)

@router.get("/sports", response_model=SportTypes, description="Get sports data")
async def get_sports(
    db: AsyncSession = Depends(get_async_db),
):
    sport_service = SportService(db, LanguageEnum.GERMAN)
    sports = await sport_service.get_sports()
    sports = SportTypes.from_table(sports)
    return sports