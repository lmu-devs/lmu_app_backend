from fastapi import APIRouter, Depends

from api.src.v1.core.language import get_language
from shared.src.enums.language_enums import LanguageEnum

from ..models.faculty_model import Faculties
from ..models.university_model import Universities
from ..services.university_service import UniversityService

router = APIRouter()


@router.get(
    "/faculties",
    response_model=Faculties,
    description="Get all faculty titles and names",
)
async def get_faculties(language: LanguageEnum = Depends(get_language)) -> Faculties:
    """Fetches all faculties with their titles and ids."""
    university_service = UniversityService(language)
    faculties = await university_service.get_faculties()
    return faculties


@router.get(
    "/universities",
    response_model=Universities,
    description="Get all universities",
)
async def get_universities(language: LanguageEnum = Depends(get_language)) -> Universities:
    university_service = UniversityService(language)
    universities = await university_service.get_universities()
    return universities
