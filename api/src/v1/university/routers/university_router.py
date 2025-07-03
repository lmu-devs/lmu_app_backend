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
async def get_faculties(accept_language: str = Header())-> Faculties:
    """Fetches all faculties with their titles and ids."""
    university_service = UniversityService(accept_language)
    faculties = await university_service.get_faculties()
    return faculties


@router.get(
    "/universities",
    response_model=Universities,
    description="Get all universities",
)
async def get_universities(accept_language: str = Header()) -> Universities:
    university_service = UniversityService(accept_language)
    universities = await university_service.get_universities()
    return universities
