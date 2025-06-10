from fastapi import APIRouter
from ..services.lecture_service import LectureService
from ..models.lecture import Lectures

router = APIRouter()


@router.get(
    "/all-lectures",
    response_model=Lectures,
    description="Get all faculty lectures",
)
async def get_lectures() -> Lectures:
    lecture_service = LectureService()
    return Lectures()
