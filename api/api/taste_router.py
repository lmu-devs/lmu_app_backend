from fastapi import APIRouter

from api.service.label_enum_service import taste_profile


router = APIRouter()


@router.get("/taste-profile")
async def get_label_presets():
    return taste_profile







