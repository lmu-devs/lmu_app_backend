from fastapi import APIRouter, Depends

from api.src.v1.clubs.models.club_model import ClubsResponse 
from api.src.v1.core.api_key import APIKey
from api.src.v1.core.language import get_language
from shared.src.core.logging import get_clubs_logger
from shared.src.enums import LanguageEnum

from ..services.clubs_service import ClubService

router = APIRouter()
logger = get_clubs_logger(__name__)


@router.get(
    "/clubs",
    response_model=ClubsResponse,
    description="Get all resources for student clubs grouped by category.",
)
async def get_all_resources(
    language: LanguageEnum = Depends(get_language),
):
    club_service = ClubService()
    return await club_service.get_clubs(language)
