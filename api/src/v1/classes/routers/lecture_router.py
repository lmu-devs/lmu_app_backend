from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db


from ..services.lecture_service import LectureService
from ..models.lecture import Lectures

router = APIRouter()


@router.get(
    "/all-lectures",
    response_model=Lectures,
    description="Get all lectures",
)
async def get_all_lectures() -> Lectures:
    lecture_service = LectureService()
    return await lecture_service.get_all_lectures()


@router.get(
    "/faculty-lectures",
    response_model=Lectures,
    description="Get all lectures from a specified faculty",
)
async def get_lectures_from(
    faculty_id: str = "MATH_INFO_STATS", db: AsyncSession = Depends(get_async_db)
) -> Lectures:
    lecture_service = LectureService()
    return await lecture_service.get_lectures_from_faculty(faculty_id, db)
