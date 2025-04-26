from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.language import get_language
from api.src.v1.link.models.link_benefits_model import LinkBenefits
from api.src.v1.link.models.link_resources_model import LinkResources
from api.src.v1.link.services.link_benefit_service import LinkBenefitService
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_links_logger
from shared.src.enums import LanguageEnum

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
):
    link_service = LinkResourceService(db, language)
    links = await link_service.get_links()
    links = LinkResources.from_table(links)
    return links


@router.get("/benefits", response_model=LinkBenefits, description="Get all student benefits")
async def get_all_benefits(
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
):
    link_benefit_service = LinkBenefitService(db, language)
    benefits = await link_benefit_service.get_benefits()
    benefits = LinkBenefits.from_table(benefits)
    return benefits
