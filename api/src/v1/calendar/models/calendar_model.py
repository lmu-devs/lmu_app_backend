from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, RootModel


class EventType(str, Enum): # not complete
    MOVIE = "MOVIE"
    SPORT = "SPORT"
    LECTURE = "LECTURE"
    EXAM = "EXAM"
    OTHER = "OTHER"

class Frequency(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class UpdateType(int, Enum):
    THIS = 0
    ALL = 2
    FUTURE = 3

class AccessScope(int, Enum):
    """Controls which user is authorized to see which event. 
    This is also sometimes useful, for example for debugging 
    and not all users should see an public event directly."""

    PERSONAL = 0 # event created by a user
    PUBLIC = 10 # event for all users
    USER = 50
    ADMIN = 100

class CalendarLocation(BaseModel):
    address: str
    latitude: float
    longitude: float

    @staticmethod
    def from_json(json: dict) -> "CalendarLocation":
        if json is None:
            return None
        
        return CalendarLocation(
            address=json["address"],
            latitude=json["latitude"],
            longitude=json["longitude"]
        )
    
    @staticmethod
    def to_json(entry: "CalendarLocation") -> dict:  
        data = {
            "address": entry.address,
            "latitude": entry.latitude,
            "longitude": entry.longitude
        }
        return data
        
class CalendarRule(BaseModel):
    frequency: Frequency
    interval: int                  # e.g. every two weeks: frequency=WEEKLY, interval=2
    until_time: Optional[datetime] # end date for repeat, used when available

    @staticmethod
    def from_json(json: dict) -> "CalendarRule":
        return CalendarRule(
            frequency=json["frequency"],
            interval=json["interval"],
            until_time=json.get("until_time")
        )

class CalendarException(BaseModel):

    @staticmethod
    def to_json(create_entry: "CalendarCreate", 
        calendar_event_id: UUID, 
        recurrence_id: int, 
        location_id: Optional[UUID] = None
        ) -> dict:
        
        loc_data = None
        if create_entry.location:
            loc_data = CalendarLocation.to_json(create_entry.location)
            if location_id:
                loc_data["id"] = str(location_id)
        
        data = {
            "title": create_entry.title,
            "description": create_entry.description,
            "location": loc_data,
            "start_time": create_entry.start_time.isoformat() if create_entry.start_time else None,
            "end_time": create_entry.end_time.isoformat() if create_entry.end_time else None,
            "all_day": create_entry.all_day,
            "recurrence_id": recurrence_id,
            "event": { "id": str(calendar_event_id) }
        }
        return data

class CalendarCreate(BaseModel):
    """
    Create a new calendar event.
    """

    title: Optional[str]
    description: Optional[str]
    location: Optional[CalendarLocation]
    rule: CalendarRule
    event_type: EventType
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    all_day: bool
    access_scope: AccessScope

    @staticmethod
    def to_json(create_entry: "CalendarCreate", 
        user_id: UUID, 
        rule_id: UUID, 
        location_id: UUID
        ) -> dict:

        rule_dict = {
            "frequency": create_entry.rule.frequency,
            "interval": create_entry.rule.interval,
            "until_time": create_entry.rule.until_time.isoformat() if create_entry.rule.until_time else None
        }

        loc_dict = None
        if create_entry.location:
            loc_dict = {
                "address": create_entry.location.address,
                "latitude": create_entry.location.latitude,
                "longitude": create_entry.location.longitude
            }
            if location_id:
                loc_dict["id"] = str(location_id)

        if rule_id:
            rule_dict["id"] = str(rule_id)
     
        return {
                "title": create_entry.title,
                "user_id": str(user_id) if user_id else None,
                "all_day": create_entry.all_day,
                "event_type": create_entry.event_type,
                "start_time": create_entry.start_time.isoformat(),
                "end_time": create_entry.end_time.isoformat(),
                "description": create_entry.description,
                "location": loc_dict,
                "rule": rule_dict,
                "access_scope": create_entry.access_scope
        }

class CalendarEvent(CalendarCreate):
    """
    Calendar event.
    """

    id: UUID
    user_id: Optional[UUID]
    recurrence_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_json(json: dict, 
        exception_data: dict = None
        ) -> "CalendarEvent":
            updated_at = json.get("date_updated") or json.get("date_created")

            rule = CalendarRule.from_json(json["rule"])
            location = CalendarLocation.from_json(json.get("location"))
           
            title = json["title"]
            description = json.get("description")
            start_time = json["start_time"]
            end_time = json["end_time"]
            all_day = json["all_day"]
            recurrence_id = None

            if exception_data:
                title = exception_data.get("title", title)
                description = exception_data.get("description", description)
                location = CalendarLocation.from_json(exception_data.get("location"))
                start_time = exception_data.get("start_time", start_time)
                end_time = exception_data.get("end_time", end_time)
                all_day = exception_data.get("all_day", all_day)
                recurrence_id = exception_data.get("recurrence_id", recurrence_id)

            return CalendarEvent(
                id=json["id"],
                user_id=json.get("user_id"),
                created_at=json["date_created"],
                updated_at=updated_at,
                title=title,
                description=description,
                location=location,
                rule=rule,
                event_type=json["event_type"],
                start_time=start_time,
                end_time=end_time,
                all_day=all_day,
                recurrence_id=recurrence_id,
                access_scope=json["access_scope"]
            )
    
    def copy_with_override(self, 
        **overrides
        ) -> "CalendarEvent":
        return self.__class__(**{**self.model_dump(), **overrides})
    
class CalendarEntries(RootModel):
    root: List[CalendarEvent]

    @classmethod
    def from_list(cls, 
        data: List[CalendarEvent]
        ) -> "CalendarEntries":
        return CalendarEntries(root=data)