from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.src.tables import UserTable
from shared.src.core.logging import get_food_logger
from shared.src.core.database import get_db
from api.src.v1.core.api_key import APIKey

from ..schemas.places_scheme import Location
# from ..services.places_service import LocationService

# router = APIRouter()
# logger = get_food_logger(__name__)

# @router.get("/location", response_model=Location, description="Get location data")
# async def get_location(
#     db: Session = Depends(get_db),
#     user: UserTable = Depends(APIKey.verify_user_api_key)
# ):
#     location_service = LocationService(db)
#     return location_service.get_location_data().model_dump()