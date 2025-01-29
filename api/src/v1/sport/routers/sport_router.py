from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.sport.pydantics.sport_pydantic import sport_types_to_pydantic
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.enums import LanguageEnum

from ..models.sport_model import SportType
from ..services.sport_service import SportService


router = APIRouter()
logger = get_places_logger(__name__)

@router.get("/sports", response_model=List[SportType], description="Get sports data")
async def get_sports(
    db: AsyncSession = Depends(get_async_db),
):
    sport_service = SportService(db, LanguageEnum.GERMAN)
    sports = await sport_service.get_sports()
    sports = await sport_types_to_pydantic(sports)
    return sports