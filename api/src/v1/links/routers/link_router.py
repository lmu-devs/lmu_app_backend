from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.language import get_language
from api.src.v1.links.models.link_benefits_model import LinkBenefits
from api.src.v1.links.models.link_resources_model import LinkResources
from api.src.v1.links.services.link_benefit_service import BenefitService
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_links_logger
from shared.src.enums import LanguageEnum

# from ..schemas.room_schema import RoomType
from ..services.link_resources_service import LinkService


router = APIRouter()
logger = get_links_logger(__name__)

@router.get("/resources", response_model=LinkResources, description="Get all Links for important LMU services")
async def get_all(
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
):
    link_service = LinkService(db, language)
    links = await link_service.get_links()
    links = LinkResources.from_table(links)
    return links

@router.get("/benefits", response_model=LinkBenefits, description="Get all benefits for important LMU services")
async def get_all(
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
):
    benefit_service = BenefitService(db, language)
    benefits = await benefit_service.get_benefits()
    benefits = LinkBenefits.from_table(benefits)
    return benefits

