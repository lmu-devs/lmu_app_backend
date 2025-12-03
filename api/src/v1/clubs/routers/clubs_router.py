from typing import List

from fastapi import APIRouter, Depends

from api.src.v1.clubs.models.club_model import Club
from api.src.v1.core.api_key import APIKey
from api.src.v1.core.language import get_language
from shared.src.core.logging import get_clubs_logger
from shared.src.enums import LanguageEnum
from shared.src.tables.user_table import UserTable

from ..services.clubs_service import ClubService

router = APIRouter()
logger = get_clubs_logger(__name__)


@router.get(
    "/clubs",
    response_model=List[Club],
    description="Get all resources for student clubs.",
)
async def get_all_resources(
    language: LanguageEnum = Depends(get_language),
):
    club_service = ClubService()
    clubs = await club_service.get_clubs(language)
    return clubs
