from datetime import datetime
from uuid import UUID
from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables import EventType, RepeatType, CalendarTable

update_blacklist: list[str] =  [ "id", "user_id", "created_at"]

class CalendarCreate(BaseModel):
    """
    Create a new calendar entry.
    """

    # event data
    title: str
    description: str | None = None
    #location: str | None = None
    event_type: EventType
    start_time: datetime
    end_time: datetime

    # repeat data
    repeat_type: RepeatType
    # repeat_interval: Integer    # every two weeks: epeat_type=WEEKLY, repeat_interval=2
    # repeat_end_time: datetime   # end date for repeat?? optional?
    # repeat_cout: Integer        # limit -> shouldn't be here since we want it dynamic 

class CalendarEntry(CalendarCreate):
    """
    Calendar entry.
    """

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_table(calendar: CalendarTable) -> "CalendarEntry":
        return CalendarEntry(
            id=calendar.id,
            user_id=calendar.user_id,
            created_at=calendar.created_at,
            updated_at=calendar.updated_at,

            title=calendar.title,
            description=calendar.description,
            event_type=calendar.event_type,
            start_time=calendar.start_time,
            end_time=calendar.end_time,
            repeat_type=calendar.repeat_type,
        )
    
class CalendarEntries(RootModel):
    root: List[CalendarEntry]

    @classmethod
    def from_table(cls, data: List[CalendarTable]) -> "CalendarEntries":
        return CalendarEntries(root=[CalendarEntry.from_table(entry) for entry in data])