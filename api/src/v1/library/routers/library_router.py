from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.core.logging import get_main_logger
from shared.src.enums import LanguageEnum
from shared.src.tables import UserTable

from ...core import APIKey
from ...core.language import get_language
from ..models.library_model import Libraries
from ..services.library_service import LibraryService

router = APIRouter()
logger = get_main_logger(__name__)


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
    language: LanguageEnum = Depends(get_language),
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[UserTable] = Depends(APIKey.verify_user_api_key_soft),
):
    library_service = LibraryService(db)

    if current_user:
        libraries = await library_service.get_libraries(id, language)
        logger.info(f"Fetched {'library' if id else 'all libraries'} with language {language.value}")
        return Libraries.from_table(libraries, current_user.id)

    libraries = await library_service.get_libraries(id, language)
    logger.info(f"Fetched {'library' if id else 'all libraries'} with language {language.value}")
    return Libraries.from_table(libraries)


@router.post(
    "/libraries/toggle-like",
    response_model=bool,
    description="Authenticated user can toggle like for a library. Returns True if the library was liked, False if it was unliked.",
)
async def toggle_like(
    library_id: str = Query(
        ...,
        description="Library ID to toggle like",
        example="1204",
        title="Library ID",
    ),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key),
) -> bool:
    library_service = LibraryService(db)
    return await library_service.toggle_like(library_id, current_user.id)
