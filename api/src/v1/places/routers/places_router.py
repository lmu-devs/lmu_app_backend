from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.tables import UserTable
from shared.src.core.logging import get_places_logger
from shared.src.core.database import get_async_db
from api.src.v1.core.api_key import APIKey

from ..schemas.places_scheme import Location
from ..services.places_service import PlacesService

router = APIRouter()
logger = get_places_logger(__name__)

@router.get("/places", response_model=Location, description="Get places data")
async def get_places(
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    places_service = PlacesService(db)
    return await places_service.get_places()
