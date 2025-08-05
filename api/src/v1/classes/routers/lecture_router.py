import datetime

from fastapi import APIRouter, Depends

from ..services.lecture_service import LectureService
from ..models.lecture import LecturesBasic, LectureDetails
from shared.src.core.database import get_async_db

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.get(
    "/course-by-faculty",
    response_model=LecturesBasic,
    description="Get all courses from a specified faculty",
)
async def get_courses_from_faculty(
    faculty_id: int = 1,
    term_id: int = 1,
    year: int = datetime.datetime.now().year,
    session: AsyncSession = Depends(get_async_db),
) -> LecturesBasic:
    """Endpoint to get course from a specific faculty."""
    lecture_service = LectureService()
    result = await lecture_service.get_lectures_from_faculty_db(
        session,
        faculty_id,
        year,
        term_id
    )
    return result


@router.get(
    "/course-details",
    response_model=LectureDetails,
    description="Get all courses from a specified faculty",
)
async def get_course_details(
    publish_id: int,
    session: AsyncSession = Depends(get_async_db),
) -> LectureDetails:
    """Endpoint to get course from a specific faculty."""
    lecture_service = LectureService()
    result = await lecture_service.get_lecture_details_db(session, publish_id)
    return result
