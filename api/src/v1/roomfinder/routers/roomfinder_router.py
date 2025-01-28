from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.sport.pydantics.sport_pydantic import sport_types_to_pydantic
from api.src.v1.roomfinder.models.room_model import Room
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.enums import LanguageEnum

# from ..schemas.room_schema import RoomType
from ..services.roomfinder_service import RoomfinderService


router = APIRouter()
logger = get_places_logger(__name__)

# @router.get("/roomfinder", response_model=List[RoomType], description="Get all roomfinder data")
# async def get_roomfinder(
#     db: AsyncSession = Depends(get_async_db),
# ):
#     roomfinder_service = RoomfinderService(db)
#     # rooms = await roomfinder_service.get_rooms()
#     # rooms = await room_types_to_pydantic(rooms)
#     return rooms


@router.get("/rooms", response_model=List[Room], description="Get all roomfinder data")
async def get_rooms(
    db: AsyncSession = Depends(get_async_db),
):
    roomfinder_service = RoomfinderService(db)
    rooms = await roomfinder_service.get_rooms()
    rooms = [Room.from_table(room) for room in rooms]
    return rooms