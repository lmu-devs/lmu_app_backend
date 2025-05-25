from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.api_key import APIKey
from api.src.v1.core.language import get_language
from api.src.v1.link.models.link_resources_model import LinkResources
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_links_logger
from shared.src.enums import LanguageEnum
from shared.src.tables.user_table import UserTable

from ..constants.benefits_constants import benefits_constants
from ..services.link_resources_service import LinkResourceService

router = APIRouter()
logger = get_links_logger(__name__)


@router.get(
    "/resources",
    response_model=LinkResources,
    description="Get all resources for important LMU services",
)
async def get_all_resources(
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
    user: UserTable = Depends(APIKey.verify_user_api_key_soft),
):
    link_service = LinkResourceService(db)
    user_id = user.id if user else None
    links = await link_service.get_links(language, user_id)
    links_model = LinkResources.from_table(links)
    return links_model


@router.get(
    "/resources/toggle-like",
    description="Toggle like for a link resource",
    response_model=bool,
)
async def toggle_like(
    id: str = Query(..., description="The id of the resource to toggle like"),
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key),
):
    link_service = LinkResourceService(db)
    is_liked = await link_service.toggle_like(id, user.id)
    return is_liked


@router.get(
    "/benefits",
    description="Get all benefits for important LMU services",
)
async def get_all_benefits(
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
):
    return benefits_constants
