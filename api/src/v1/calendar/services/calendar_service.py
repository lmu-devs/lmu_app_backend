import uuid
import json
from typing import Optional
from enum import Enum
from datetime import timedelta
from pathlib import Path
from dateutil.relativedelta import relativedelta
from shared.src.core.exceptions import DatabaseError

from api.src.v1.calendar.models.calendar_model import (
    Frequency, 
    CalendarEntry, 
    CalendarCreate, 
    UpdateType,
    CalendarException
)

from shared.src.core.logging import get_calendar_logger
from shared.src.services.directus_service import DirectusService

logger = get_calendar_logger(__name__)

REPEAT_LIMIT: int = 5  # default limit, used if until_time == None
GRAPHQL_DIR = Path(__file__).parent.parent / "graphql"

class GraphQLFile(str, Enum):
    kCreate = "create_calendar_event.graphql"
    kDelete = "delete_calendar_event.graphql"
    kUpdate = "update_calendar_event.graphql"
    kGetEvent = "get_calendar_event.graphql"
    kGetInformation = "get_calendar_information.graphql"
    kCreateException = "create_calendar_exception.graphql"
    kUpdateException = "update_calendar_exception.graphql"
    kDeleteException = "delete_calendar_exception.graphql"

class CalendarService:
    def __init__(self):
        self.directus = DirectusService()

    def _get_graphql_file(self, file: GraphQLFile) -> Path:
        return GRAPHQL_DIR / file.value
   
    def _get_delta(self, 
        frequency: Frequency, 
        interval: int
        ):

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
            
    def _safe_get(self, data: dict, path: list, default=None):
        try:
            for key in path:
                if isinstance(data, list):
                    data = data[key]
                else:
                    data = data.get(key)
            return data
        except (KeyError, IndexError, TypeError):
            return default

    def _get_entry_information(self, entry_id: uuid.UUID, file: GraphQLFile) -> dict: 
            
        filters = {
            "id": {"_eq": str(entry_id)}
        }
   
        response = self.directus.execute_query_file(
            query_file_path=self._get_graphql_file(file),
            variables={"filter": filters}
        )

        if (errors := response.get("errors")):
            raise DatabaseError(f"Failed to get entry information: {errors}")
            
        return response
         
    def _generate_repeat_events(self, 
        parent_event: CalendarEntry, 
        max_past: int = REPEAT_LIMIT,
        max_future: int = REPEAT_LIMIT, 
        ) -> list[CalendarEntry]:
            
        if parent_event is None:
            return []
         
        rule = parent_event.rule
        if not rule or rule.frequency == Frequency.ONCE:
            return [parent_event]
        
        delta = self._get_delta(rule.frequency, rule.interval or 1)
        if delta is None:
            return [parent_event]

        base_start = parent_event.start_time
        base_end = parent_event.end_time

        # past events
        past = []
        for i in range(max_past, 0, -1):
            start, end = base_start - i * delta, base_end - i * delta
            if not rule.until_time or end >= rule.until_time:
               past.append(parent_event.copy_with_override(start_time=start, end_time=end, recurrence_id=-i))

        # future events
        future = []
        for i in range(1, max_future + 1):
            start, end = base_start + i * delta, base_end + i * delta
            if rule.until_time and start > rule.until_time:
                break

            future.append(parent_event.copy_with_override(start_time=start, end_time=end, recurrence_id=i))
        
        parent_event.recurrence_id = 0
        return past + [parent_event] + future

    def create_calendar_entry(self, 
        user_id: uuid.UUID, 
        calendar_data: CalendarCreate
        ) -> list[CalendarEntry]:
          
        create_entry = CalendarCreate.to_json(calendar_data, user_id, None)   

        response = self.directus.execute_query_file(
            query_file_path=self._get_graphql_file(GraphQLFile.kCreate),
            variables={"data": create_entry},
        )

        if (errors := response.get("errors")):
            raise DatabaseError(f"Failed to create calendar entry: {errors}")

        #logger.info("Response:\n%s", json.dumps(response, indent=2))

        item = response.get("data", {}).get("create_calendar_event_item", {})
        if not item:
            raise DatabaseError("Failed to create calendar entry! No calendar item returned from GraphQL!")

        entry = CalendarEntry.from_json(item)

        logger.info( f"Created new calendar entry {entry.id} for user {user_id}")
        return self._generate_repeat_events(entry)

    def delete_calendar_entry(self, 
        entry_id: uuid.UUID
        ) -> bool:
            
        if not entry_id:
            logger.error(f"Failed to remove calendar entry: entry_id is null")
            return False
        
        response = self._get_entry_information(entry_id, GraphQLFile.kGetInformation)      
        calendar_event = self._safe_get(response, ["data", "calendar_event", 0])
        if not calendar_event:
            logger.warning(f"No calendar event found with ID {entry_id}")
            return False
        
        rule_id = self._safe_get(calendar_event, ["rule", "id"])
        exceptions = calendar_event.get("exceptions", [])
        if not rule_id:
            logger.warning(f"No rule found for calendar event {entry_id}")
            return False
        
        event_response = self.directus.execute_query_file(
            query_file_path=self._get_graphql_file(GraphQLFile.kDelete),
            variables={
                "eventId": str(entry_id),
                "ruleId": str(rule_id)
                },
            )

        if (errors := event_response.get("errors")):
            raise DatabaseError(f"Failed to remove calendar entry: {errors}")

        for exc in exceptions:
            exc_id = exc.get("id")
            if not exc_id:
                continue

            delete_exc_response = self.directus.execute_query_file(
                query_file_path=self._get_graphql_file(GraphQLFile.kDeleteException),
                variables={ "id": exc_id }
            )       

            if (errors := delete_exc_response.get("errors")):
                logger.error(f"Failed to delete exception {exc_id}: {errors}")

        #logger.info(f"Deleted calendar entry {entry_id} with rule {rule_id}")
        return True
     
    def _update_entry(self,
        user_id: uuid.UUID, 
        entry_id: uuid.UUID,     
        update_data: CalendarCreate,                   
        ) -> CalendarEntry:

        rule_response = self._get_entry_information(entry_id, GraphQLFile.kGetInformation)        
        rule_id = self._safe_get(rule_response, ["data", "calendar_event", 0, "rule", "id"])

        if rule_id is None:
            logger.warning(f"No rule found for calendar event {entry_id}")
            return None

        update_response = self.directus.execute_query_file(
        query_file_path=self._get_graphql_file(GraphQLFile.kUpdate),
        variables={
            "id": str(entry_id),
            "data": CalendarCreate.to_json(update_data, user_id, rule_id)
             },
        )

        if (errors := update_response.get("errors")):
            raise DatabaseError(f"Failed to update calendar entry: {errors}")

        item = update_response.get("data", {}).get("update_calendar_event_item", {})

        logger.info(f"Updated calendar entry {entry_id} for user {user_id}")
        return CalendarEntry.from_json(item)
   
    def _get_exception_id_from_response(self, response: dict, recurrence_id: int) -> Optional[str]:
        exceptions = self._safe_get(response, ["data", "calendar_event", 0, "exceptions"], default=[])
        for entry in exceptions:
            if entry.get("recurrence_id") == recurrence_id:
                return entry.get("id")
        return None

    def _update_repeat_entry(self,
        entry_id: uuid.UUID,     
        update_data: CalendarCreate,  
        recurrence_id: int                 
        ) -> list[CalendarEntry]:

        response = self._get_entry_information(entry_id, GraphQLFile.kGetEvent)  
        #logger.info("First Response:\n%s", json.dumps(response, indent=2))
        
        exception_id = self._get_exception_id_from_response(response, recurrence_id)

        if exception_id:
            logger.info("Update")
            mutation_path = self._get_graphql_file(GraphQLFile.kUpdateException)
            variables = {
                "id": exception_id,
                "data": CalendarException.to_json(update_data, entry_id, recurrence_id)
            }
        else:
            mutation_path = self._get_graphql_file(GraphQLFile.kCreateException)
            variables = {
                "data": CalendarException.to_json(update_data, entry_id, recurrence_id)
            }

        update_response = self.directus.execute_query_file(
            query_file_path=mutation_path,
            variables=variables
        )

        #logger.info("Second Response:\n%s", json.dumps(update_response, indent=2))

        if (errors := update_response.get("errors")):
            raise DatabaseError(f"Failed to update calendar entry: {errors}")

        base_event = response.get("data", {}).get("calendar_event", [])
        exception_data = update_response.get("data", {}).get("update_calendar_exceptions_item") \
                            or update_response.get("data", {}).get("create_calendar_exceptions_item")


        logger.info(f"Updated repeat event {recurrence_id} for calendar entry {entry_id}")
        return [CalendarEntry.from_json(base_event[0], exception_data)]

    def update_calendar_entry(self, 
        user_id: uuid.UUID, 
        entry_id: uuid.UUID, 
        recurrence_id: int,
        update_data: CalendarCreate, 
        update_type: UpdateType
        ) -> list[CalendarEntry]:
        
        if recurrence_id is None:
            update_type = UpdateType.ALL

        match update_type:
            case UpdateType.THIS: # only use for repeat frequencies, call Update.All for ONCE
                # generate an overwrite and attach
                return self._update_repeat_entry(entry_id, update_data, recurrence_id)
            case UpdateType.ALL:
                updated_entry = self._update_entry(user_id, entry_id, update_data)
                return self._generate_repeat_events(updated_entry)
            case UpdateType.FUTURE: # split 
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
        
        filters = {
            "user_id": {"_eq": str(user_id)}
        }

        if event_type:
            filters["event_type"] = {"_eq": event_type}
        if all_day is not None:
            filters["all_day"] = {"_eq": all_day}
        if frequency:
            filters["rule"] = {"frequency": {"_eq": frequency}}

        response = self.directus.execute_query_file(
            query_file_path=self._get_graphql_file(GraphQLFile.kGetEvent),
            variables={"filter": filters}
        )
        
        if (errors := response.get("errors")):
                raise DatabaseError(f"Failed to get calendar entries: {errors}")

        base_events = response.get("data", {}).get("calendar_event", [])

        instances = []
        for event in base_events:
            calendar_entry = CalendarEntry.from_json(event)
            instances.extend(self._generate_repeat_events(calendar_entry))

        return instances