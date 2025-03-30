from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.roomfinder.models.street_model import Streets
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger

from ..services.roomfinder_service import RoomfinderService


router = APIRouter()
logger = get_places_logger(__name__)

@router.get("/all", response_model=Streets, description="Get all Streets, Buildings, Floors, Rooms")
async def get_all(
    db: AsyncSession = Depends(get_async_db),
):
    roomfinder_service = RoomfinderService(db)
    cities = await roomfinder_service.get_all()
    cities = Streets.from_table(cities)
    return cities