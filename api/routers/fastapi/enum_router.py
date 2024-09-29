from typing import List
from fastapi import APIRouter

from api.models.label_model import LabelDto
from api.service.label_enum_service import labels, labels_sorted, label_presets


router = APIRouter()


# Gets labels
@router.get("/enums/labels", response_model=List[LabelDto])
async def get_labels():
    return labels

@router.get("/enums/labels-sorted")
async def get_labels_sorted():
    return labels_sorted

@router.get("/enums/label-presets")
async def get_label_presets():
    return label_presets







