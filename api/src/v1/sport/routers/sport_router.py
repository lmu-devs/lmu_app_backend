from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.api_key import APIKey
from api.src.v1.core.language import get_language
from api.src.v1.sport.pydantics.sport_pydantic import sport_types_to_pydantic
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.enums import LanguageEnum
from shared.src.tables.user_table import UserTable

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

@router.post("/sports/toggle-like", response_model=bool, description="Toggle like for a sport course")
async def toggle_like(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key),
    language: LanguageEnum = Depends(get_language)
):
    sport_service = SportService(db, language)
    return await sport_service.toggle_like(id, user.id)