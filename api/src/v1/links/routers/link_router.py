from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from api.src.v1.core.language import get_language
from api.src.v1.links.models.link_model import Links
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_links_logger
from shared.src.enums import LanguageEnum

# from ..schemas.room_schema import RoomType
from ..services.link_service import LinkService


router = APIRouter()
logger = get_links_logger(__name__)

@router.get("/links", response_model=Links, description="Get all Links for important LMU services")
async def get_all(
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
):
    link_service = LinkService(db, language)
    links = await link_service.get_links()
    links = Links.from_table(links)
    return links

