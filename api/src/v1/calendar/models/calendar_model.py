from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shared.src.tables import EventType, RepeatType, CalendarTable

update_blacklist: list[str] =  [ "id", "user_id", "created_at"]

class CalendarCreate(BaseModel):
    """
    Create a new calendar entry.
    """

    # event data
    title: str | None = None
    description: str | None = None
    #location: str | None = None
    event_type: EventType | None = None
    start_time: datetime
    end_time: datetime

    # repeat data
    repeat_type: RepeatType
    # repeat_interval: Integer    # every two weeks: epeat_type=WEEKLY, repeat_interval=2
    # repeat_end_time: datetime   # end date for repeat?? optional?
    # repeat_cout: Integer        # limit -> shouldn't be here since we want it dynamic 

class Calendar(CalendarCreate):
    """
    Calendar entry.
    """

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_table(calendar: CalendarTable) -> "Calendar":
        return Calendar(
            id=calendar.id,
            user_id=calendar.user_id,
            created_at=calendar.created_at,
            updated_at=calendar.updated_at,

            title=calendar.title,
            description=calendar.description,
            event_type=calendar.event_type,
            start_time=calendar.start_time,
            end_time=calendar.end_time,
            repeat_type=calendar.repeat_type
        )