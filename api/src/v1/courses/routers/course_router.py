import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.courses.models.semesters import SemestersModel
from shared.src.core.database import get_async_db
from shared.src.enums.courses_enums import SemesterEnum

from ..models.course import CourseDetails, CoursesBasic
from ..services.course_service import CourseService

router = APIRouter()


@router.get(
    "/by-faculty",
    response_model=CoursesBasic,
    description="Get all courses from a specified faculty",
)
async def get_courses_from_faculty(
    faculty_id: int = 1,
    semester_type: SemesterEnum = SemesterEnum.WINTER,
    year: int = datetime.datetime.now().year,
    session: AsyncSession = Depends(get_async_db),
) -> CoursesBasic:
    """Endpoint to get course from a specific faculty."""
    course_service = CourseService()
    result = await course_service.get_courses_from_faculty_db(session, faculty_id, year, semester_type)
    return result


@router.get(
    "/details",
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


@router.get(
    "/available-semesters",
    response_model=SemestersModel,
    description="Get all available semesters",
)
async def get_available_semesters(
    session: AsyncSession = Depends(get_async_db),
) -> SemestersModel:
    """Endpoint to get all available semesters."""
    course_service = CourseService()
    return await course_service.get_available_semesters_db(session)
