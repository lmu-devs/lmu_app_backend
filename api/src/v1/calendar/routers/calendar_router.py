import uuid

from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.api_key import APIKey
from api.src.v1.calendar.models.calendar_model import CalendarCreate, CalendarEntry,CalendarEntries
from api.src.v1.calendar.services.calendar_service import CalendarService
from shared.src.core.database import get_async_db
from shared.src.tables import UserTable

router = APIRouter()

@router.post("/calendar-create", response_model=CalendarEntries, description="Create a calendar entry.")
async def create_calendar_entry(
    calendar_data: CalendarCreate,
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key),
):
    calendar_service = CalendarService(db)
    entries = await calendar_service.create_calendar_entry(user.id, calendar_data.model_dump())
    return CalendarEntries.from_table(entries)

@router.delete("/calendar-remove", response_model=bool, description="Remove a calendar entry")
async def remove_calendar_entry(
    db: AsyncSession = Depends(get_async_db),
    entry_id: uuid.UUID = None,
    user: UserTable = Depends(APIKey.verify_user_api_key),
):
    calendar_service = CalendarService(db)
    success = await calendar_service.remove_calendar_entry(user.id, entry_id)
    return success

@router.put("/calendar-update", response_model=CalendarEntries, description="Update a calendar entry")
async def update_calendar_entry(
    calendar_data: CalendarCreate,
    db: AsyncSession = Depends(get_async_db),
    entry_id: uuid.UUID = None,
    user: UserTable = Depends(APIKey.verify_user_api_key),
):
    calendar_service = CalendarService(db)
    entries = await calendar_service.update_calendar_entry(user.id, entry_id, calendar_data.model_dump())
    return CalendarEntries.from_table(entries)

@router.get("/calendar-get", response_model=CalendarEntries, description="Get all calendar entries for a user. Optional with a filter.")
async def get_calendar_entries(
    db: AsyncSession = Depends(get_async_db),
    user: UserTable = Depends(APIKey.verify_user_api_key),
    event_type: Optional[str] = None,
    repeat_type: Optional[str] = None,
    all_day: Optional[bool] = None
):
    
    calendar_service = CalendarService(db)
    entries = await calendar_service.get_all_with_repeats(user.id, event_type, repeat_type, all_day)
    return CalendarEntries.from_table(entries)
