from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.roomfinder.models.city_model import Cities
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger

from ..services.roomfinder_service import RoomfinderService


router = APIRouter()
logger = get_places_logger(__name__)

@router.get("/all", response_model=Cities, description="Get all Cities, Streets, Buildings, Floors, Rooms")
async def get_all(
    db: AsyncSession = Depends(get_async_db),
):
    roomfinder_service = RoomfinderService(db)
    cities = await roomfinder_service.get_all()
    cities = Cities.from_table(cities)
    return cities