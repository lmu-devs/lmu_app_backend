import uuid

from typing import Optional

from fastapi import APIRouter, Depends

from api.src.v1.calendar.models.calendar_model import (
    AccessScope,
    CalendarCreate,
    CalendarEntries,
    EventType,
    UpdateType,
)
from api.src.v1.calendar.services.calendar_service import CalendarService
from api.src.v1.core.api_key import APIKey

from shared.src.tables import UserTable

router = APIRouter()

@router.post("/calendar-create-user", response_model=CalendarEntries, description="Create a calendar event for an user.")
async def create_event_user(
    calendar_data: CalendarCreate,
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    entries = CalendarService().create_event(user.id, calendar_data)
    return CalendarEntries.from_list(entries)

@router.post("/calendar-create-public", response_model=CalendarEntries, description="Create a calendar event for all users.")
async def create_event_public(
    calendar_data: CalendarCreate,
):
    entries = CalendarService().create_event(None, calendar_data)
    return CalendarEntries.from_list(entries)

@router.put("/calendar-update", response_model=CalendarEntries, description="Update a calendar event.")
async def update_event(
    calendar_data: CalendarCreate,
    event_id: uuid.UUID,
    recurrence_id: Optional[int] = None,
    update_type: UpdateType = UpdateType.THIS,
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    entries = CalendarService().update_event(user.id, event_id, recurrence_id, calendar_data, update_type)
    return CalendarEntries.from_list(entries)

@router.put("/calendar-update-public", response_model=CalendarEntries, description="Update a calendar event available for all users.")
async def update_event(
    calendar_data: CalendarCreate,
    event_id: uuid.UUID,
    recurrence_id: Optional[int] = None,
    update_type: UpdateType = UpdateType.THIS
):
    entries = CalendarService().update_event(None, event_id, recurrence_id, calendar_data, update_type)
    return CalendarEntries.from_list(entries)

@router.delete("/calendar-delete/{event_id}", response_model=bool, description="Delete a calendar event.")
async def delete_event(
    event_id: uuid.UUID
):
    return CalendarService().delete_event(event_id)

@router.get("/calendar-get", response_model=CalendarEntries, description="Get all calendar events for a user. Optional with a filter.")
async def get_events(
    event_type: Optional[EventType] = None,
    frequency: Optional[str] = None,
    all_day: Optional[bool] = None,
    access_scope: AccessScope = AccessScope.USER,
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    events = CalendarService().get_all(user.id, access_scope, event_type, frequency, all_day)
    return CalendarEntries.from_list(events)
