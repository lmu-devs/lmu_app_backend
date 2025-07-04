import uuid
from typing import Optional
from enum import Enum
from datetime import timedelta, datetime
from pathlib import Path
from dateutil.relativedelta import relativedelta
from shared.src.core.exceptions import DatabaseError

from api.src.v1.calendar.models.calendar_model import (
    Frequency, 
    CalendarEntry, 
    CalendarCreate, 
    UpdateType,
    CalendarException,
    CalendarLocation
)

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

    def _get_entry_information(self, 
        entry_id: uuid.UUID, 
        file: GraphQLFile,
        path: list
        ) -> Optional[dict]:
        """Retrieves a specific entry from the database via a GraphQL file. The information contained may vary depending on the file."""
        filters = {
            "id": {"_eq": str(entry_id)}
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
         
    def _generate_repeat_events(self, 
        parent_event: dict, 
        max_past: int = REPEAT_LIMIT,
        max_future: int = REPEAT_LIMIT, 
        ) -> list[CalendarEntry]:
        """Generates all recurring event instances based on a parent event and its recurrence rule. 
        If there are exceptions, they will overwrite the corresponding event."""
        if parent_event is None:
            return []
        
        parent_entry = CalendarEntry.from_json(parent_event)
        rule = parent_entry.rule
        if not rule or rule.frequency == Frequency.ONCE:
            return [parent_entry]
        
        delta = self._get_delta(rule.frequency, rule.interval or 1)
        if delta is None:
            return [parent_entry]
    
        raw_exceptions = self._safe_get(parent_event, ["exceptions"]) or []
        exceptions_map = {
            exc.get("recurrence_id"): exc
            for exc in raw_exceptions
            if "recurrence_id" in exc
        }

        base_start = parent_entry.start_time
        base_end = parent_entry.end_time
        result = []

        # helper
        def generate_entry(offset: int, start: datetime, end: datetime) -> CalendarEntry:
            if offset in exceptions_map:
                return CalendarEntry.from_json(parent_event, exceptions_map[offset])
            return parent_entry.copy_with_override(start_time=start, end_time=end, recurrence_id=offset)

        # past events
        for i in range(max_past, 0, -1):
            start, end = base_start - i * delta, base_end - i * delta
            if not rule.until_time or end >= rule.until_time:
               result.append(generate_entry(-i, start, end))

        # base event
        if 0 in exceptions_map:
            entry = CalendarEntry.from_json(parent_event, exceptions_map[0])
        else:
            entry = parent_entry
        entry.recurrence_id = 0
        result.append(entry)

        # future events
        for i in range(1, max_future + 1):
            start, end = base_start + i * delta, base_end + i * delta
            if rule.until_time and start > rule.until_time:
                break
            result.append(generate_entry(i, start, end))
        
        return result
    
    def _delete_location_entry(self,
        location_id: uuid.UUID
        ):
        if location_id:
            location_delete = self._execute_graphql_file(GraphQLFile.kDeleteLocation, { "locationId": str(location_id) }, [])
            if not location_delete:
                raise DatabaseError(f"Failed to delete location {location_id}!")

    def _delete_related_entry(self,
        entry_id: uuid.UUID, 
        information: dict                     
        ):
        """Deletes the entry and some related entries to the calendar entry."""
        rule_id = self._safe_get(information, ["rule", "id"])
        
        rule_delete = self._execute_graphql_file(GraphQLFile.kDelete, { "eventId": str(entry_id), "ruleId": str(rule_id) }, [])
        if not rule_delete:
            raise DatabaseError(f"Failed to delete {entry_id} and {rule_id}!")
        
        location_id = self._safe_get(information, ["location", "id"])
        self._delete_location_entry(location_id)

    def create_entry(self, 
        user_id: uuid.UUID, 
        calendar_data: CalendarCreate
        ) -> list[CalendarEntry]:
        """Creates a calendar entry in the database. Returns a list of several recurring events based on the event rule."""  
        create_entry = CalendarCreate.to_json(calendar_data, user_id, None, None)   

        item = self._execute_graphql_file(GraphQLFile.kCreate, {"data": create_entry}, ["create_calendar_event_item"])
        if not item:
            raise DatabaseError("Failed to create calendar entry!")

        logger.info( f"Created new calendar entry {item["id"]} for user {user_id}")
        return self._generate_repeat_events(item)

    def delete_entry(self, 
        entry_id: uuid.UUID
        ) -> bool:
        """Deletes a calendar entry from the database."""    
        information = self._get_entry_information(entry_id, GraphQLFile.kGetInformation, ["calendar_event", 0])      
        if not information:
            raise DatabaseError(f"No calendar event found with ID {entry_id}")
        
        self._delete_related_entry(entry_id, information)

        exceptions = information.get("exceptions", [])
        for exc in exceptions:
            exc_location_id = self._safe_get(exc, ["location", "id"])
            self._delete_location_entry(exc_location_id)

            exc_id = exc.get("id")
            exc_delete = self._execute_graphql_file(GraphQLFile.kDeleteException, {"exceptionId": exc_id}, [])
            if not exc_delete:
                raise DatabaseError(f"Failed to delete exception {exc_id}")

        logger.info(f"Deleted calendar entry {entry_id}!")
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
            self._delete_location_entry(old_id)
            return None

        if not old_id:
            # new address added
            return None

        return old_id  # address unchanged, updated

    def _update_entry(self,
        user_id: uuid.UUID, 
        entry_id: uuid.UUID,     
        update_data: CalendarCreate,                   
        ) -> list[CalendarEntry]:
        """Performs an update to the base event instance. Therefore all events are updated."""
        event = self._get_entry_information(entry_id, GraphQLFile.kGetInformation, ["calendar_event", 0])        
        if not event:
            raise DatabaseError(f"Failed to update {entry_id}! No information returned!")

        rule_id = self._safe_get(event, ["rule", "id"])
        location = self._safe_get(event, ["location"])
        new_location_id = self._handle_location_update(location, update_data.location)
        json_data = CalendarCreate.to_json(update_data, user_id, rule_id, new_location_id)

        item = self._execute_graphql_file(GraphQLFile.kUpdate, {"id": str(entry_id),"data": json_data}, ["update_calendar_event_item"])
        if not item:
            raise DatabaseError(f"Failed to update {entry_id}!")
        
        return self._generate_repeat_events(item)

    def _update_repeat_entry(self,
        entry_id: uuid.UUID,     
        update_data: CalendarCreate,  
        recurrence_id: int                 
        ) -> list[CalendarEntry]:
        """Performs an update to a generated event instance. Therefore a new exception is created or the existing one is updated."""
        event = self._get_entry_information(entry_id, GraphQLFile.kGetEvent, ["calendar_event", 0]) 
        if not event:
            raise DatabaseError(f"Failed to update {entry_id}! No information returned!")

        exception = self._get_exception_by_id(event.get("exceptions"), recurrence_id)

        if exception:
            file = GraphQLFile.kUpdateException
            exc_location_id = self._handle_location_update(exception.get("location"), update_data.location) 
            variables = {
                "id": exception.get("id"),
                "data": CalendarException.to_json(update_data, entry_id, recurrence_id, exc_location_id)
            }
        else:
            file = GraphQLFile.kCreateException
            variables = {
                "data": CalendarException.to_json(update_data, entry_id, recurrence_id)  
            }

        item = self._execute_graphql_file(file, variables, [])
        if not item:
            raise DatabaseError(f"Failed to update {entry_id}!")

        exception_data = item.get("update_calendar_exceptions_item") \
                            or item.get("create_calendar_exceptions_item")

        return [CalendarEntry.from_json(event, exception_data)]

    def update_entry(self, 
        user_id: uuid.UUID, 
        entry_id: uuid.UUID, 
        recurrence_id: int,
        update_data: CalendarCreate, 
        update_type: UpdateType
        ) -> list[CalendarEntry]:
        """Updates calendar entries in the database."""
        if recurrence_id is None:
            update_type = UpdateType.ALL

        match update_type:
            case UpdateType.THIS: # only use for repeat frequencies, call Update.All for ONCE
                # generate an overwrite and attach
                logger.info(f"Updating single occurrence of calendar entry {entry_id} for user {user_id}")
                return self._update_repeat_entry(entry_id, update_data, recurrence_id)
            case UpdateType.ALL:
                logger.info(f"Updating all occurrences of calendar entry {entry_id} for user {user_id}")
                return self._update_entry(user_id, entry_id, update_data)
            case UpdateType.FUTURE: # split 
                logger.info("Not implemented yet!")
                return []
            case _:
                logger.warning(f"Unknown update type: {update_type}")
                return []
    
    def get_all(
        self,
        user_id: uuid.UUID,
        event_type: Optional[str] = None,
        frequency: Optional[str] = None,
        all_day: Optional[bool] = None
    ) -> list[CalendarEntry]:
        """Returns a list of all calendar entries for a user. Several filters are optionally available."""
        filters = {
            "user_id": {"_eq": str(user_id)}
        }

        if event_type:
            filters["event_type"] = {"_eq": event_type}
        if all_day is not None:
            filters["all_day"] = {"_eq": all_day}
        if frequency:
            filters["rule"] = {"frequency": {"_eq": frequency}}

        events = self._execute_graphql_file(GraphQLFile.kGetEvent, {"filter": filters}, ["calendar_event"])
        if not events:
            logger.error("No entries found!")

        instances = []
        for event in events:
            instances.extend(self._generate_repeat_events(event))

        return instances