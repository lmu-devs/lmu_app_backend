import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db

from ..models.course import CourseDetails, CoursesBasic
from ..services.course_service import CourseService

router = APIRouter()


@router.get(
    "/course-by-faculty",
    response_model=CoursesBasic,
    description="Get all courses from a specified faculty",
)
async def get_courses_from_faculty(
    faculty_id: int = 1,
    term_id: int = 1,
    year: int = datetime.datetime.now().year,
    session: AsyncSession = Depends(get_async_db),
) -> CoursesBasic:
    """Endpoint to get course from a specific faculty."""
    course_service = CourseService()
    result = await course_service.get_courses_from_faculty_db(session, faculty_id, year, term_id)
    return result


@router.get(
    "/course-details",
    response_model=CourseDetails,
    description="Get all courses from a specified faculty",
)
async def get_course_details(
    publish_id: int,
    session: AsyncSession = Depends(get_async_db),
) -> CourseDetails:
    """Endpoint to get course from a specific faculty."""
    course_service = CourseService()
    result = await course_service.getcourse_details_db(session, publish_id)
    return result
