import uuid
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, RootModel
from enum import Enum
from typing import Dict

class EventType(str, Enum): # not complete
    MOVIE = "MOVIE"
    SPORT = "SPORT"
    LECTURE = "LECTURE"
    EXAM = "EXAM"

class Frequency(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class UpdateType(int, Enum):
    THIS = 0
    ALL = 1
    FUTURE = 2

class CalendarLocation(BaseModel):
    address: str
    latitude: float
    longitude: float

    @staticmethod
    def from_json(json: Dict) -> "CalendarLocation":
        if json is None:
            return None
        
        return CalendarLocation(
            address=json["address"],
            latitude=json["latitude"],
            longitude=json["longitude"]
        )
    
    @staticmethod
    def to_json(entry: "CalendarLocation") -> Dict:  
        data = {
            "address": entry.address,
            "latitude": entry.latitude,
            "longitude": entry.longitude
        }
        return data
        
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

class CalendarException(BaseModel):

    @staticmethod
    def to_json(create_entry: "CalendarCreate", 
        calendar_event_id: UUID, 
        recurrence_id: int, 
        location_id: Optional[UUID] = None
        ) -> Dict:
        
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
    Create a new calendar entry.
    """

    title: Optional[str]
    description: Optional[str]
    location: Optional[CalendarLocation]
    rule: CalendarRule
    event_type: EventType
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    all_day: bool

    @staticmethod
    def to_json(create_entry: "CalendarCreate", 
        user_id: uuid.UUID, 
        rule_id: uuid.UUID, 
        location_id: uuid.UUID
        ) -> Dict:

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
                "rule": rule_dict
        }

class CalendarEntry(CalendarCreate):
    """
    Calendar entry.
    """

    id: UUID
    user_id: UUID
    recurrence_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_json(json: Dict, 
        exception_data: Dict = None
        ) -> "CalendarEntry":
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
                location_exc = CalendarLocation.from_json(exception_data.get("location"))
                if location_exc:
                    location = location_exc

                start_time = exception_data.get("start_time", start_time)
                end_time = exception_data.get("end_time", end_time)
                all_day = exception_data.get("all_day", all_day)
                recurrence_id = exception_data.get("recurrence_id", recurrence_id)

            return CalendarEntry(
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
            )
    
    def copy_with_override(self, 
        **overrides
        ) -> "CalendarEntry":
        return self.__class__(**{**self.model_dump(), **overrides})
    
class CalendarEntries(RootModel):
    root: List[CalendarEntry]

    @classmethod
    def from_list(cls, 
        data: List[CalendarEntry]
        ) -> "CalendarEntries":
        return CalendarEntries(root=data)