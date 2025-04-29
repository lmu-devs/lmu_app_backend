from fastapi import APIRouter, Query

from api.src.v1.map.models.map_model import ThemeEnum
from shared.src.core.logging import get_places_logger

from ..services.map_service import MapService

router = APIRouter()
logger = get_places_logger(__name__)


@router.get("/style", response_model=dict, description="Get map style")
async def get_places(
    theme: ThemeEnum = Query(ThemeEnum.LIGHT, description="Theme of the map"),
):
    map_service = MapService()
    places = await map_service.get_map_style(theme)
    return places
