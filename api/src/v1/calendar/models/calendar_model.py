import uuid
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, RootModel
from enum import Enum
from typing import Dict
from shared.src.core.logging import get_calendar_logger

REPEAT_LIMIT: int = 10  # default limit, used if until_time == None

logger = get_calendar_logger(__name__)

class EventType(str, Enum): # not complete
    MOVIE = "MOVIE"
    SPORT = "SPORT"
    LECTURE = "LECTURE"

class Frequency(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class CalendarRule(BaseModel):
    frequency: Frequency
    interval: int                  # e.g. every two weeks: repeat_type=WEEKLY, repeat_interval=2
    until_time: Optional[datetime] # end date for repeat, used when available. Otherwise the REPEAT_LIMIT is used

    @staticmethod
    def from_json(json: Dict) -> "CalendarRule":
        return CalendarRule(
            frequency=json["frequency"],
            interval=json["interval"],
            until_time=json.get("until_time")
        )


class CalendarCreate(BaseModel):
    """
    Create a new calendar entry.
    """

    title: str
    description: Optional[str]
    address: Optional[str]
    rule: CalendarRule
    event_type: EventType
    start_time: datetime
    end_time: datetime
    all_day: bool

    @staticmethod
    def to_json(create_entry: "CalendarCreate", user_id: uuid.UUID) -> Dict:
        return {
                "title": create_entry.title,
                "user_id": str(user_id),
                "all_day": create_entry.all_day,
                "event_type": create_entry.event_type,
                "start_time": create_entry.start_time.isoformat(),
                "end_time": create_entry.end_time.isoformat(),
                "description": create_entry.description,
                "address": create_entry.address,
                "rule": {
                    "frequency": create_entry.rule.frequency,
                    "interval": create_entry.rule.interval,
                    "until_time": create_entry.rule.until_time.isoformat() if create_entry.rule.until_time else None
                }
        }

class CalendarEntry(CalendarCreate):
    """
    Calendar entry.
    """

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_json(json: Dict) -> "CalendarEntry":    
            updated_at = json.get("date_updated")
            if updated_at is None:
                updated_at = json.get("date_created")

            rule_data = json.get("rule")
            rule = CalendarRule.from_json(rule_data[0])
            
            return CalendarEntry(
                id=json["id"],
                user_id=json["user_id"],
                created_at=json["date_created"],
                updated_at=updated_at,
                title=json["title"],
                description=json.get("description"),
                address=json.get("address"),
                rule=rule,
                event_type=json["event_type"],
                start_time=json["start_time"],
                end_time=json["end_time"],
                all_day=json["all_day"]
            )
    
class CalendarEntries(RootModel):
    root: List[CalendarEntry]

    @classmethod
    def from_list(cls, data: List[CalendarEntry]) -> "CalendarEntries":
        return CalendarEntries(root=data)