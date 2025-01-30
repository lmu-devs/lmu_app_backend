from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.core.logging import get_places_logger
from shared.src.enums import LanguageEnum

from ..models.timeline_model import Timeline
from ..services.timeline_service import TimelineService


router = APIRouter()
logger = get_places_logger(__name__)

@router.get("/timeline", response_model=Timeline, description="Get timeline data")
async def get_timeline(
    db: AsyncSession = Depends(get_async_db),
):
    timeline_service = TimelineService(db)
    timeline = await timeline_service.get_timeline()
    return timeline