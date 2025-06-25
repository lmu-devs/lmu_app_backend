import uuid

from fastapi import APIRouter, Depends
from typing import Optional

from api.src.v1.core.api_key import APIKey
from api.src.v1.calendar.models.calendar_model import CalendarCreate, CalendarEntries
from api.src.v1.calendar.services.calendar_service import CalendarService
from shared.src.tables import UserTable

router = APIRouter()

@router.post("/calendar-create", response_model=CalendarEntries, description="Create a calendar entry.")
async def create_calendar_entry(
    calendar_data: CalendarCreate,
    user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    entries = CalendarService().create_calendar_entry(user.id, calendar_data)
    return CalendarEntries.from_list(entries)

@router.delete("/calendar-delete", response_model=bool, description="Delete a calendar entry.")
async def delete_calendar_entry(
    entry_id: uuid.UUID
):
    return CalendarService().delete_calendar_entry(entry_id)

@router.put("/calendar-update", response_model=CalendarEntries, description="Update a calendar entry.")
async def update_calendar_entry(
    calendar_data: CalendarCreate,
    entry_id: uuid.UUID,
    recurrence_id: Optional[int] = None,
    update_type: int = 0,
    user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    entries = CalendarService().update_calendar_entry(user.id, entry_id, recurrence_id, calendar_data, update_type)
    return CalendarEntries.from_list(entries)

@router.get("/calendar-get", response_model=CalendarEntries, description="Get all calendar entries for a user. Optional with a filter.")
async def get_calendar_entries(
    event_type: Optional[str] = None,
    frequency: Optional[str] = None,
    all_day: Optional[bool] = None,
    user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    entries = CalendarService().get_all(user.id, event_type, frequency, all_day)
    return CalendarEntries.from_list(entries)
