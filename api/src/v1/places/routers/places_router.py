from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.api_key import APIKey
from api.src.v1.places.pydantics.places_pydantic import places_to_pydantic
from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.tables import UserTable

from ..schemas.places_scheme import Place
from ..services.places_service import PlacesService


router = APIRouter()
logger = get_places_logger(__name__)

@router.get("/places", response_model=List[Place], description="Get places data")
async def get_places(
    db: AsyncSession = Depends(get_async_db),
):
    places_service = PlacesService(db)
    places = await places_service.get_places()
    places = await places_to_pydantic(places)
    return places