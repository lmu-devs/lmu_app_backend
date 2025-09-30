import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Response, Query

from api.src.v1.calendar.models.calendar_model import (
    AccessScope,
    CalendarCreate,
    CalendarEntries,
    CalendarException,
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
async def update_event_user(
    event_id: uuid.UUID,
    calendar_exception: CalendarException,
    update_type: UpdateType = UpdateType.ALL,
    recurrence_id: Optional[int] = None,
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    entries = CalendarService().update_event(user.id, event_id, recurrence_id, calendar_exception, update_type)
    return CalendarEntries.from_list(entries)

@router.put("/calendar-update-public", response_model=CalendarEntries, description="Update a calendar event available for all users.")
async def update_event_public(
    event_id: uuid.UUID,
    calendar_exception: CalendarException,
    update_type: UpdateType = UpdateType.ALL,
    recurrence_id: Optional[int] = None
):
    entries = CalendarService().update_event(None, event_id, recurrence_id, calendar_exception, update_type)
    return CalendarEntries.from_list(entries)

@router.delete("/calendar-delete", response_model=bool, description="Delete a calendar event.")
async def delete_event(
    event_id: uuid.UUID,
    recurrence_id: Optional[int] = None
):
    return CalendarService().delete_event(event_id, recurrence_id)

@router.get("/calendar-get", response_model=CalendarEntries, description="Get all calendar events for a user. Optional with a filter.")
async def get_events(
    event_type: Optional[EventType] = None,
    frequency: Optional[str] = None,
    all_day: Optional[bool] = None,
    access_scope: list[AccessScope] = Query([AccessScope.PERSONAL, AccessScope.PUBLIC]),
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    events = CalendarService().get_all(user.id, access_scope, True, event_type, frequency, all_day)
    return CalendarEntries.from_list(events)

@router.get("/calendar/ical/{access_scope_str}--{user_id}.ics", description="Public iCal feed for a user's events.")
async def get_user_ical_feed(
    access_scope_str: str,
    user_id: uuid.UUID
    ):
    access_scopes = [AccessScope(int(x)) for x in access_scope_str.split(",")]
    return Response(content=CalendarService().generate_ical(user_id, access_scopes), media_type="text/calendar")