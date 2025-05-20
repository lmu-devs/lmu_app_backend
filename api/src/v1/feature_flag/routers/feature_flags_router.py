from typing import List

from fastapi import APIRouter
from fastapi.params import Query

from api.src.v1.feature_flag.models.feature_flags_model import FeatureFlagResponse
from api.src.v1.feature_flag.services.feature_flags_service import FeatureFlagService

router = APIRouter()


@router.get(
    "/feature-flags",
    response_model=List[FeatureFlagResponse],
    description="Get all feature flags",
)
async def get_all_resources(
    version: str = Query(..., description="The version of the feature flag"),
):
    feature_flag_service = FeatureFlagService(version)
    feature_flags = await feature_flag_service.get_feature_flags()
    return feature_flags
