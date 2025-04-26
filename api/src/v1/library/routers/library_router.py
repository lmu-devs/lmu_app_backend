from typing import Optional

from fastapi import APIRouter, Query

from ..models.library_model import Libraries
from ..services.library_service import LibraryService

router = APIRouter()
library_service = LibraryService()


@router.get(
    "/libraries",
    response_model=Libraries,
    description="Get all libraries or a specific library by ID",
)
async def get_libraries(
    id: Optional[str] = Query(
        None,
        description="Specific library ID to fetch",
        example="1204",
        title="Library ID",
    ),
):
    return library_service.get_libraries(id)
