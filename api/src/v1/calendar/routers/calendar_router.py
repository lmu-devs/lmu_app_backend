import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response

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

@router.post("/user-event", response_model=CalendarEntries, description="Create a calendar event for a user.")
async def create_event_user(
    calendar_data: CalendarCreate, 
    current_date: Optional[datetime] = None,
    user: UserTable = Depends(APIKey.verify_user_api_key)
): 
    events = CalendarService().create_event(
        user_id=user.id, 
        calendar_data=calendar_data, 
        current_date=current_date
    )

    return CalendarEntries.from_list(events)

@router.put("/user-event", response_model=CalendarEntries, description="Update a calendar event for a user.")
async def update_event_user(
    event_id: uuid.UUID,
    calendar_exception: CalendarException,
    update_type: UpdateType = UpdateType.ALL,
    recurrence_id: Optional[int] = None,
    current_date: Optional[datetime] = None,
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    events = CalendarService().update_event(
        user_id=user.id,
        event_id=event_id,
        recurrence_id=recurrence_id,
        update_exception=calendar_exception,
        update_type=update_type,
        current_date=current_date
    )

    return CalendarEntries.from_list(events)

@router.delete("/user-event", response_model=bool, description="Delete a user calendar event.")
async def delete_event_user(
    event_id: uuid.UUID, 
    recurrence_id: Optional[int] = None,
    user: UserTable = Depends(APIKey.verify_user_api_key)
):
    return CalendarService().delete_event(user_id=user.id,event_id=event_id, recurrence_id=recurrence_id)


@router.post("/public-event", response_model=CalendarEntries, description="Create a calendar event for all users.")
async def create_event_public(
    calendar_data: CalendarCreate,
    current_date: Optional[datetime] = None,
    authorized: bool = Depends(APIKey.verify_admin_api_key)
):
    events = CalendarService().create_event(
        user_id=None, 
        calendar_data=calendar_data, 
        current_date=current_date
    )

    return CalendarEntries.from_list(events)

@router.put(
    "/public-event",
    response_model=CalendarEntries,
    description="Update a calendar event that is available to all users.",
)
async def update_event_public(
    event_id: uuid.UUID,
    calendar_exception: CalendarException,
    update_type: UpdateType = UpdateType.ALL,
    recurrence_id: Optional[int] = None,
    current_date: Optional[datetime] = None,
    authorized: bool = Depends(APIKey.verify_admin_api_key)
):
    events = CalendarService().update_event(
        user_id=None,
        event_id=event_id,
        recurrence_id=recurrence_id,
        update_exception=calendar_exception,
        update_type=update_type,
        current_date=current_date
    )

    return CalendarEntries.from_list(events)

@router.delete("/public-event", response_model=bool, description="Delete a public calendar event.")
async def delete_event_public(
    event_id: uuid.UUID, 
    recurrence_id: Optional[int] = None,
    authorized: bool = Depends(APIKey.verify_admin_api_key)
):
    return CalendarService().delete_event(user_id=None, event_id=event_id, recurrence_id=recurrence_id)


@router.get(
    "/get",
    response_model=CalendarEntries,
    description="Retrieve all calendar events for a user. Pass None as user to only get all the public events. Optionally with multiple filters.",
)
async def get_events(
    event_type: Optional[EventType] = None,
    frequency: Optional[str] = None,
    all_day: Optional[bool] = None,
    access_scope: list[AccessScope] = Query([AccessScope.PERSONAL, AccessScope.PUBLIC]),
    current_date: Optional[datetime] = None,
    user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    user_id = user.id if user else None
    access_scope = access_scope if user else [AccessScope.PUBLIC]

    events = CalendarService().get_all(
        user_id=user_id,
        access_scope=access_scope,
        generate_recurrence=True,
        event_type=event_type,
        frequency=frequency,
        all_day=all_day,
        current_date=current_date
    )

    return CalendarEntries.from_list(events)

@router.get("/ical/{access_scope_str}--{user_id}.ics", description="Public iCal feed for a user's events.")
async def get_user_ical_feed(
    access_scope_str: str, # Hyphen-separated string, e.g. "0-10"  -- if there's a better option than this please fix
    user_id: uuid.UUID
):
    events = CalendarService().generate_ical(user_id=user_id, access_scope_str=access_scope_str)
    return Response(content=events, media_type="text/calendar")