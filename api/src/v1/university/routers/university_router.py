from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db

from ..models.university_model import Universities
from ..models.faculty_model import Faculties
from ..services.university_service import UniversityService


router = APIRouter()


@router.get(
    "/faculties",
    response_model=Faculties,
    description="Get all faculty titles and names",
)
async def get_faculties(languagecode: str = "de-DE"):
    university_service = UniversityService(languagecode)
    faculties = await university_service.get_faculties()
    return faculties


@router.get(
    "/universities",
    response_model=Universities,
    description="Get all universities",
)
async def get_universities(language_code: str = "de-DE"):
    university_service = UniversityService(language_code)
    university_service = await university_service.get_universities()
    return university_service
