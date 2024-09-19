from typing import List
from fastapi import APIRouter

from api.models.label_model import LabelDto
from api.service.label_enum_service import labels


router = APIRouter()


# Gets labels
@router.get("/enums/labels", response_model=List[LabelDto])
async def get_label():
    return labels







