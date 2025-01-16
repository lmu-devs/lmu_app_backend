from fastapi import APIRouter, Depends

from shared.src.enums import LanguageEnum

from ...core.language import get_language
from ..services.label_enum_service import translate_taste_profile


router = APIRouter()

@router.get("/taste-profile", description="Get all taste profile labels with presets for vegetarian, vegan dishes and more.")
async def get_label_presets(language: LanguageEnum = Depends(get_language)):
    return translate_taste_profile(language)







