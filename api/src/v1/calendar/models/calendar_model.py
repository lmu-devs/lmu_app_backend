from datetime import datetime
from uuid import UUID
from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables import EventType, RepeatType, CalendarTable

UPDATE_BLACKLIST: list[str] =  [ "id", "user_id", "created_at"] # items that should not be updated
REPEAT_LIMIT: int = 10  # default limit, used if repeat_end_time == None

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
    all_day: bool = False

    # repeat data
    repeat_type: RepeatType
    repeat_interval: int | None = None          # e.g. every two weeks: repeat_type=WEEKLY, repeat_interval=2
    repeat_end_time: datetime | None = None     # end date for repeat, used when available. Otherwise the REPEAT_LIMIT is used

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
            all_day=calendar.all_day,

            repeat_type=calendar.repeat_type,
            repeat_interval=calendar.repeat_interval,
            repeat_end_time=calendar.repeat_end_time
        )
    
class CalendarEntries(RootModel):
    root: List[CalendarEntry]

    @classmethod
    def from_table(cls, data: List[CalendarTable]) -> "CalendarEntries":
        return CalendarEntries(root=[CalendarEntry.from_table(entry) for entry in data])