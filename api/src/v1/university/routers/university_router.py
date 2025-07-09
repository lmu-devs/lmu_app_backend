from fastapi import Header, APIRouter

from ..models.university_model import Universities
from ..models.faculty_model import Faculties
from ..services.university_service import UniversityService

router = APIRouter()


@router.get(
    "/faculties",
    response_model=Faculties,
    description="Get all faculty titles and names",
)
async def get_faculties(accept_language: str = Header("de-DE"))-> Faculties:
    """Fetches all faculties with their titles and ids."""
    language = map_language(accept_language)
    university_service = UniversityService(language)
    faculties = await university_service.get_faculties()
    return faculties


@router.get(
    "/universities",
    response_model=Universities,
    description="Get all universities",
)
async def get_universities(accept_language: str = Header("de-DE")) -> Universities:
    language = map_language(accept_language)
    university_service = UniversityService(language)
    universities = await university_service.get_universities()
    return universities

def map_language(language: str) -> str:
    if language == "de":
        return "de-DE"
    elif language == "en":
        return "en-US"
    else:
        return language
