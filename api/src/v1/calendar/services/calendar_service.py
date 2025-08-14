import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from dateutil.relativedelta import relativedelta
from typing import Optional
from icalendar import Calendar, Event

from api.src.v1.calendar.models.calendar_model import (
    AccessScope,
    CalendarCreate,
    CalendarEvent,
    CalendarException,
    CalendarLocation,
    Frequency,
    UpdateType,
)

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_calendar_logger
from shared.src.services.directus_service import DirectusService

logger = get_calendar_logger(__name__)

REPEAT_LIMIT: int = 5  # default limit, used if until_time == None
GRAPHQL_DIR = Path(__file__).parent.parent / "graphql"

class GraphQLFile(str, Enum):
    kCreate = "create_event"
    kDelete = "delete_event"
    kUpdate = "update_event"
    kGetEvent = "get_event"
    kGetInformation = "get_information"
    kCreateException = "create_exception"
    kUpdateException = "update_exception"
    kDeleteException = "delete_exception"
    kDeleteLocation = "delete_location"

class CalendarService:
    def __init__(self):
        self.directus = DirectusService()

    def _get_graphql_file(self, 
        file: GraphQLFile
        ) -> Path:
        """Returns the path to the GraphQL file based on the enum value."""
        return GRAPHQL_DIR / f"{file.value}.graphql"
   
    def _get_delta(self, 
        frequency: Frequency, 
        interval: int
        ):
        """Calculates the time delta based on frequency and interval value."""
        match frequency:
            case Frequency.DAILY:
                return timedelta(days=interval)
            case Frequency.WEEKLY:
                return timedelta(weeks=interval)
            case Frequency.MONTHLY:
                return relativedelta(months=interval)
            case Frequency.YEARLY:
                return relativedelta(years=interval)
            case _:
                return None
            
    def _safe_get(self, 
        data: dict, 
        path: list
        ) -> Optional[dict]:
        """Safely retrieves a nested value from a dictionary using a sequence of keys."""
        try:
            for key in path:
                if isinstance(data, dict):
                    data = data.get(key)
                elif isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
                    data = data[key]
                else:
                    return None
            return data
        except Exception:
            return None
        
    def _execute_graphql_file(self,
        file: GraphQLFile,
        variables: dict,
        path: list
        ) -> Optional[dict]:
        """Executes a GraphQL file with safety checks and the "data" stripped out."""  
        try:        
            response = self.directus.execute_query_file(self._get_graphql_file(file), variables)
        except Exception as e:
            raise DatabaseError(f"Exception while executing GraphQL file {file}: {e}") from e

        if (errors := response.get("errors")):
            raise DatabaseError(f"Errors while executing GraphQL file {file}: {errors}")
        
        return self._safe_get(response, ["data"] + path)

    def _get_event_information(self, 
        event_id: uuid.UUID, 
        file: GraphQLFile,
        path: list
        ) -> Optional[dict]:
        """Retrieves a specific event from the database via a GraphQL file. The information contained may vary depending on the file."""
        filters = {
            "id": {"_eq": str(event_id)}
        }
   
        return self._execute_graphql_file(file, {"filter": filters}, path)
    
    def _get_exception_by_id(self, 
        exceptions: dict, 
        recurrence_id: int
        ) -> Optional[str]:
        """Returns the exception entry ID from the dict for a given recurrence ID."""
        if not exceptions:
            return None

        for entry in exceptions:
            if entry.get("recurrence_id") == recurrence_id:
                return entry
        return None
         
    def _calc_intervals_since_start(self, 
        start: datetime, 
        now: datetime, delta) -> int:
        """Calculates the number of intervals happend between now and the start time."""
        if isinstance(delta, timedelta):
            return (now - start) // delta
        elif isinstance(delta, relativedelta):
            # months or years
            months_diff = (now.year - start.year) * 12 + (now.month - start.month)
            if delta.years:
                interval_months = delta.years * 12
            else:
                interval_months = delta.months
            return months_diff // interval_months
        else:
            return 0

    def _generate_recurring_events(self, 
        parent_event: dict, 
        max_past: int = REPEAT_LIMIT,
        max_future: int = REPEAT_LIMIT, 
        ) -> list[CalendarEvent]:
        """Generates all recurring event instances based on a parent event and its recurrence rule. 
        If there are exceptions, they will overwrite the corresponding event."""
        if parent_event is None:
            return []
        
        template = CalendarEvent.from_json(parent_event)
        rule = template.rule
        if rule.frequency == Frequency.ONCE:
            return [template]
        
        delta = self._get_delta(rule.frequency, rule.interval or 1)
        if delta is None:
            return [template]
        
        raw_exceptions = self._safe_get(parent_event, ["exceptions"]) or []
        exceptions_map = { exc.get("recurrence_id"): exc for exc in raw_exceptions if "recurrence_id" in exc }

        event_duration = template.end_time - template.start_time
        intervals_since_start = self._calc_intervals_since_start(template.start_time, datetime.now(), delta)
        
        # Prevent the creation of events that shouldn't exist if we create an event in the future
        if intervals_since_start < 0:
            intervals_since_start = 0
            current_start = template.start_time
        else:
            current_start = template.start_time + intervals_since_start * delta

        current_end = current_start + event_duration

        # helper
        def generate_entry(offset: int, start: datetime, end: datetime) -> CalendarEvent:
            exc = exceptions_map.get(offset)
            if exc:
                return CalendarEvent.from_json(parent_event, exc)
            return template.copy_with_override(start_time=start, end_time=end, recurrence_id=offset)

        result = []

        # past
        # only create past events if the event is not in the future
        for i in range(min(max_past, intervals_since_start), 0, -1):
            past_start = current_start - i * delta 
            past_end = past_start + event_duration
            if past_start >= template.start_time:
                recurrence_id = intervals_since_start - i
                result.append(generate_entry(recurrence_id, past_start, past_end))
      
        # "today"
        recurrence_id = intervals_since_start
        result.append(generate_entry(recurrence_id, current_start, current_end))

        # future
        for i in range(1, max_future + 1):
            future_start = current_start + i * delta
            future_end = future_start + event_duration
            if rule.until_time and future_start > rule.until_time: # TODO: invent new exception system :(
                break
            recurrence_id = intervals_since_start + i
            result.append(generate_entry(recurrence_id, future_start, future_end))

        return result
    
    def create_event(self, 
        user_id: uuid.UUID, 
        calendar_data: CalendarCreate
        ) -> list[CalendarEvent]:
        """Creates a calendar event in the database. Returns a list of several recurring events based on the event rule."""  
        create_event = CalendarCreate.to_json(calendar_data, user_id, None, None)   

        item = self._execute_graphql_file(GraphQLFile.kCreate, {"data": create_event}, ["create_calendar_event_item"])
        if not item:
            raise DatabaseError("Failed to create calendar event!")

        msg = "for all users!"
        if user_id:
            msg = f"for user {user_id}!"

        logger.info(f"Created new calendar event {item["id"]} {msg}")
        return self._generate_recurring_events(item, 0)
    
    def _delete_location_event(self,
        location_id: uuid.UUID
        ):
        if location_id:
            location_delete = self._execute_graphql_file(GraphQLFile.kDeleteLocation, { "locationId": str(location_id) }, [])
            if not location_delete:
                raise DatabaseError(f"Failed to delete location {location_id}!")

    def _delete_related_event(self,
        event_id: uuid.UUID, 
        information: dict                     
        ):
        """Deletes the event and some related entries to the calendar event."""
        rule_id = self._safe_get(information, ["rule", "id"])
        
        rule_delete = self._execute_graphql_file(GraphQLFile.kDelete, { "eventId": str(event_id), "ruleId": str(rule_id) }, [])
        if not rule_delete:
            raise DatabaseError(f"Failed to delete {event_id} and {rule_id}!")
        
        location_id = self._safe_get(information, ["location", "id"])
        self._delete_location_event(location_id)

    def delete_event(self, 
        event_id: uuid.UUID
        ) -> bool:
        """Deletes a calendar event from the database."""    
        information = self._get_event_information(event_id, GraphQLFile.kGetInformation, ["calendar_event", 0])      
        if not information:
            raise DatabaseError(f"No calendar event found with ID {event_id}")
        
        exceptions = information.get("exceptions", [])
        for exc in exceptions:
            exc_location_id = self._safe_get(exc, ["location", "id"])
            self._delete_location_event(exc_location_id)

        self._delete_related_event(event_id, information)

        logger.info(f"Deleted calendar event {event_id}!")
        return True
     
    def _handle_location_update(
        self,
        old_location: Optional[dict],
        new_address: Optional[CalendarLocation]
        ) -> Optional[str]:
        """Handles creation, update or deletion of the location and returns the final location_id (or None). Btw fuck GraphQL"""
        old_id = old_location.get("id") if old_location else None

        if not new_address:
            # address removed
            self._delete_location_event(old_id)
            return None

        if not old_id:
            # new address added
            return None

        return old_id  # address unchanged, updated

    def _update_event(self,
        user_id: uuid.UUID, 
        event_id: uuid.UUID,     
        update_data: CalendarCreate,                   
        ) -> list[CalendarEvent]:
        """Performs an update to the base event instance. Therefore all events are updated."""
        event = self._get_event_information(event_id, GraphQLFile.kGetInformation, ["calendar_event", 0])        
        if not event:
            raise DatabaseError(f"Failed to update {event_id}! No information returned!")

        rule_id = self._safe_get(event, ["rule", "id"])
        location = self._safe_get(event, ["location"])
        new_location_id = self._handle_location_update(location, update_data.location)
        json_data = CalendarCreate.to_json(update_data, user_id, rule_id, new_location_id)

        item = self._execute_graphql_file(GraphQLFile.kUpdate, {"id": str(event_id),"data": json_data}, ["update_calendar_event_item"])
        if not item:
            raise DatabaseError(f"Failed to update {event_id}!")
        
        return self._generate_recurring_events(item)

    def _update_repeat_event(self,
        event_id: uuid.UUID,     
        update_data: CalendarCreate,  
        recurrence_id: int                 
        ) -> list[CalendarEvent]:
        """Performs an update to a generated event instance. Therefore a new exception is created or the existing one is updated."""
        event = self._get_event_information(event_id, GraphQLFile.kGetEvent, ["calendar_event", 0]) 
        if not event:
            raise DatabaseError(f"Failed to update {event_id}! No information returned!")

        exception = self._get_exception_by_id(event.get("exceptions"), recurrence_id)

        if exception:
            file = GraphQLFile.kUpdateException
            exc_location_id = self._handle_location_update(exception.get("location"), update_data.location) 
            variables = {
                "id": exception.get("id"),
                "data": CalendarException.to_json(update_data, event_id, recurrence_id, exc_location_id)
            }
        else:
            file = GraphQLFile.kCreateException
            variables = {
                "data": CalendarException.to_json(update_data, event_id, recurrence_id)  
            }

        item = self._execute_graphql_file(file, variables, [])
        if not item:
            raise DatabaseError(f"Failed to update {event_id}!")

        exception_data = item.get("update_calendar_exceptions_item") \
                            or item.get("create_calendar_exceptions_item")

        return [CalendarEvent.from_json(event, exception_data)]

    def update_event(self, 
        user_id: uuid.UUID, 
        event_id: uuid.UUID, 
        recurrence_id: int,
        update_data: CalendarCreate, 
        update_type: UpdateType
        ) -> list[CalendarEvent]:
        """Updates calendar entries in the database."""
        if recurrence_id is None:
            update_type = UpdateType.ALL

        match update_type:
            case UpdateType.THIS: # only use for repeat frequencies, call Update.All for ONCE
                logger.info(f"Updating single occurrence of calendar event {event_id}.")
                return self._update_repeat_event(event_id, update_data, recurrence_id)
            case UpdateType.ALL:
                logger.info(f"Updating all occurrences of calendar event {event_id}.")
                return self._update_event(user_id, event_id, update_data)
            case UpdateType.FUTURE: # split 
                logger.info("Not implemented yet!")
                return []
            case _:
                logger.warning(f"Unknown update type: {update_type}")
                return []
    
    def get_all(self,
        user_id: uuid.UUID,
        access_scope: AccessScope,
        event_type: Optional[str] = None,
        frequency: Optional[str] = None,
        all_day: Optional[bool] = None
    ) -> list[CalendarEvent]:
        """Returns a list of all calendar events for a user. Several filters are optionally available. Includes global events with access_scope <= given level."""
        
        user_filter = {
            "_or": [
                {"user_id": {"_eq": str(user_id)}},
                {"user_id": {"_null": True}}
            ]
        }

        access_scope_filter = {
            "access_scope": {"_lte": access_scope}
        }

        filters = {
            "_and": [
                user_filter,
                access_scope_filter
            ]
        }
        
        if event_type:
            filters["_and"].append({"event_type": {"_eq": event_type}})
        if all_day is not None:
            filters["_and"].append({"all_day": {"_eq": all_day}})
        if frequency:
            filters["_and"].append({"rule": {"frequency": {"_eq": frequency}}})

        events = self._execute_graphql_file(GraphQLFile.kGetEvent, {"filter": filters}, ["calendar_event"])
        if not events:
            logger.error("No entries found!")

        instances = []
        for event in events:
            instances.extend(self._generate_recurring_events(event))

        return instances

    def _calendar_event_to_ical(self,
        event: CalendarEvent
    ) -> Event:

        ical_event = Event()
        ical_event.add("summary", event.title)

        uid = f"{event.id}"
        if event.recurrence_id is not None:
            uid += f"-recurrence-{event.recurrence_id}"

        ical_event.add("uid", uid)
        ical_event.add("dtstamp", event.created_at)

        if event.all_day:
            ical_event.add("dtstart", event.start_time.date())
            ical_event.add("dtend", event.end_time.date())
        else:
            ical_event.add("dtstart", event.start_time)
            ical_event.add("dtend", event.end_time)

        if event.description:
            ical_event.add("description", event.description)

        if event.location:
            ical_event.add("location", event.location.address)

        return ical_event

    def generate_ical(self, 
        user_id: uuid.UUID
        ) -> bytes:
        """Generates an iCal file with all events for a specific user."""
        if not user_id:
            raise DatabaseError(f"Got ical request with user_id = None!")
        
        cal = Calendar()
        cal.add("prodid", "-//lmu-devs//LMU Students//EN")
        cal.add("version", "2.0")
        cal.add("method", "PUBLISH")

        for event in self.get_all(user_id, AccessScope.USER):
            ical_event = self._calendar_event_to_ical(event)
            cal.add_component(ical_event)

        return cal.to_ical()