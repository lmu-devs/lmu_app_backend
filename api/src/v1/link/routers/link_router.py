from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.api_key import APIKey
from api.src.v1.core.language import get_language
from api.src.v1.link.models.link_model import Link
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_links_logger
from shared.src.enums import LanguageEnum
from shared.src.tables.user_table import UserTable

from ..services.link_service import LinkService

router = APIRouter()
logger = get_links_logger(__name__)


@router.get(
    "/resources",
    response_model=List[Link],
    description="Get all resources for important LMU services",
)
async def get_all_resources(
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
    user: UserTable = Depends(APIKey.verify_user_api_key_soft),
):
    link_service = LinkService(db)
    user_id = user.id if user else None
    links = await link_service.get_links(language, user_id)
    return links


@router.post(
    "/resources/toggle-like",
    description="Toggle like for a link resource",
    response_model=bool,
)
async def toggle_like(
    id: str = Query(..., description="The id of the resource to toggle like"),
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key),
):
    link_service = LinkService(db)
    is_liked = await link_service.toggle_like(id, user.id)
    return is_liked
