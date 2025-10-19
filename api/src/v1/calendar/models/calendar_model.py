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
    ALL = 1
    FUTURE = 2

class AccessScope(int, Enum):
    """Controls which user is authorized to see which event. 
    This is also sometimes useful, for example for debugging 
    and not all users should see an public event directly."""

    PERSONAL = 0 # event created by a user
    PUBLIC = 10 # event for all users
    ADMIN = 100 # debug scope

class RepresentationType(int, Enum):
    """Used in the exception system to determine which variable should be overwritten."""
    TITLE = 0
    DESCRIPTION = 1
    ALL_DAY = 2
    START_TIME = 3
    END_TIME = 4
    LOCATION = 5

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
    
class CalendarException(BaseModel):
    """
    Used for overwriting specific events of a recurring event.
    """

    data: CalendarCreate
    overwrite: Optional[list[RepresentationType]]

    def _get_exception_overwrite(
        exception: dict,
        new_overwrite: list[RepresentationType]
    ) -> list[str]:
        """
        Merge existing overwrite with new_overwrite, avoiding duplicates. 
        Return as string list because of the type that is used in directus.
        """
        if not new_overwrite:
            return []

        if not exception:
            return [str(x.value) for x in new_overwrite]

        overwrite = [RepresentationType(int(x)) for x in exception.get("overwrite", []) or []]

        merged = set(overwrite) | set(new_overwrite)
        return [str(x.value) for x in merged]
    
    def _merge_field(
        field: str,
        overwrite: list[RepresentationType],
        update_exception: "CalendarException",
        original_exception: Optional[dict]
    ):
        """Merge a single field with overwrite logic."""
        field_type = RepresentationType[field.upper()]

        if field_type in overwrite:
            return getattr(update_exception.data, field, None)
        if original_exception and field in original_exception:
            return original_exception.get(field)
        return None

    @staticmethod
    def to_json(update_exception: "CalendarException", 
        original_exception: Optional[str],
        calendar_event_id: UUID, 
        recurrence_id: int, 
        location_id: Optional[UUID] = None
        ) -> dict:
        
        overwrite = update_exception.overwrite
        data = update_exception.data

        loc_data = None
        if RepresentationType.LOCATION in overwrite:
            if data.location:
                loc_data = CalendarLocation.to_json(data.location)
                if location_id:
                    loc_data["id"] = str(location_id)
        elif original_exception and original_exception.get("location"):
            loc_data = original_exception.get("location")

        fields = ["title", "description", "start_time", "end_time", "all_day"]
        merged_fields = {
            field: CalendarException._merge_field(field, overwrite, update_exception, original_exception)
            for field in fields
        }

        data = {
            **merged_fields,
            "location": loc_data,
            "recurrence_id": recurrence_id,
            "overwrite": CalendarException._get_exception_overwrite(original_exception, update_exception.overwrite),
            "event": { "id": str(calendar_event_id) }
        }
        return data

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
    def from_json(json: dict, exception_data: dict = None) -> "CalendarEvent":
        updated_at = json.get("date_updated") or json.get("date_created")

        rule = CalendarRule.from_json(json["rule"])
        location = CalendarLocation.from_json(json.get("location"))

        event_data = {
            "title": json["title"],
            "description": json.get("description"),
            "start_time": json["start_time"],
            "end_time": json["end_time"],
            "all_day": json["all_day"],
            "location": location,
            "recurrence_id": None,
        }

        if exception_data:
            overwrite = {RepresentationType(int(x)) for x in exception_data.get("overwrite", []) or []}

            for field in ["title", "description", "start_time", "end_time", "all_day"]:
                field_type = RepresentationType[field.upper()]
                if field_type in overwrite:
                    event_data[field] = exception_data.get(field, event_data[field])

            if RepresentationType.LOCATION in overwrite:
                event_data["location"] = CalendarLocation.from_json(exception_data.get("location"))

            event_data["recurrence_id"] = exception_data.get("recurrence_id", event_data["recurrence_id"])

        return CalendarEvent(
            id=json["id"],
            user_id=json.get("user_id"),
            created_at=json["date_created"],
            updated_at=updated_at,
            rule=rule,
            event_type=json["event_type"],
            access_scope=json["access_scope"],
            **event_data,
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