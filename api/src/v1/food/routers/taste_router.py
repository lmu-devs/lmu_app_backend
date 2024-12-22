from fastapi import APIRouter

from ..services import taste_profile


router = APIRouter()


@router.get("/taste-profile", description="Get all taste profile labels with presets for vegetarian, vegan dishes and more.")
async def get_label_presets():
    return taste_profile







