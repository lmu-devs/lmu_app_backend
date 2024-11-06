from fastapi import APIRouter

from api.service.label_enum_service import taste_profile


router = APIRouter()


# @router.get("/enums/labels", response_model=List[LabelDto])
# async def get_labels():
#     return labels

# @router.get("/enums/labels-sorted")
# async def get_labels_sorted():
#     return labels_sorted

# @router.get("/enums/label-presets")
# async def get_label_presets():
#     return label_presets

@router.get("/taste-profile")
async def get_label_presets():
    return taste_profile







