# from typing import List
# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# from api.src.v1.core.api_key import APIKey
# from api.src.v1.sport.pydantics.sports_pydantic import sports_to_pydantic
# from shared.src.core.database import get_async_db
# from shared.src.core.logging import get_places_logger
# from shared.src.tables import UserTable

# from ..schemas.sports_scheme import Sports
# from ..services.sports_service import SportsService


# router = APIRouter()
# logger = get_places_logger(__name__)

# @router.get("/sports", response_model=List[Sports], description="Get sports data")
# async def get_sports(
#     db: AsyncSession = Depends(get_async_db),
# ):
#     sports_service = SportsService(db)
#     sports = await sports_service.get_sports()
#     sports = await sports_to_pydantic(sports)
#     return sports