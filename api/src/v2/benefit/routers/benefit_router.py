from fastapi import APIRouter, Depends

from api.src.v2.benefit.models.benefits_model import BenefitResponse
from api.src.v2.benefit.services.benefit_service import BenefitService
from api.src.v2.core.language import get_language
from shared.src.core.logging import get_links_logger
from shared.src.enums import LanguageEnum

router = APIRouter()
logger = get_links_logger(__name__)


@router.get("/benefits", description="Get all student benefits", response_model=BenefitResponse)
async def get_all_benefits(
    language: LanguageEnum = Depends(get_language),
):
    benefit_service = BenefitService(language)
    benefits = await benefit_service.get_benefits()
    return benefits
