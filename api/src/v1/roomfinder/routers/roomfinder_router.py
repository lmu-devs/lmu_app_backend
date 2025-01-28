from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.sport.pydantics.sport_pydantic import sport_types_to_pydantic
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.enums import LanguageEnum

# from ..schemas.room_schema import RoomType
# from ..services.room_service import RoomService


router = APIRouter()
logger = get_places_logger(__name__)

# @router.get("/roomfinder", response_model=List[RoomType], description="Get all roomfinder data")
# async def get_roomfinder(
#     db: AsyncSession = Depends(get_async_db),
# ):
#     room_service = RoomService(db, LanguageEnum.GERMAN)
#     rooms = await room_service.get_rooms()
#     rooms = await room_types_to_pydantic(rooms)
#     return rooms