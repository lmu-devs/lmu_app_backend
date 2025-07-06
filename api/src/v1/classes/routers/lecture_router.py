from fastapi import APIRouter

from ..services.lecture_service import LectureService
from ..models.lecture import Lectures

router = APIRouter()


@router.get(
    "/course-by-faculty",
    response_model=Lectures,
    description="Get all courses from a specified faculty",
)
async def get_courses_from_faculty(
    faculty_id: int = 1,
) -> Lectures:
    """Endpoint to get course from a specific faculty."""
    lecture_service = LectureService()
    return await lecture_service.get_lectures_from_faculty(faculty_id)
