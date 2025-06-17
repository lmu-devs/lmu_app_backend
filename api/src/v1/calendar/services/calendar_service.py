import uuid
from typing import Optional
from datetime import timedelta
from pathlib import Path
from dateutil.relativedelta import relativedelta

from api.src.v1.calendar.models.calendar_model import REPEAT_LIMIT, Frequency, CalendarEntry, CalendarCreate

from shared.src.core.logging import get_calendar_logger
from shared.src.services.directus_service import DirectusService

logger = get_calendar_logger(__name__)

class CalendarService:
    def __init__(self):
        self.directus = DirectusService()

    def get_graphql_path(self, file: str) -> Path:
        return Path(__file__).parent.parent / "graphql" / file

    def create_calendar_entry(self, user_id: uuid.UUID, calendar_data: CalendarCreate) -> list[CalendarEntry]:
            create_entry = CalendarCreate.to_json(calendar_data, user_id)   
            query_path = self.get_graphql_path("create_calendar_event.graphql")

            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"data": create_entry},
            )

            if response.get("errors"):
                raise Exception(f"Failed to create calendar entry: {response['errors']}")

            item = response.get("data", {}).get("create_calendar_event_item", {})
            entry = CalendarEntry.from_json(item)

            #logger.info( f"Created new calendar entry {entry} for user {user_id}")
            return self.generate_repeat_events(entry)

    def delete_calendar_entry(self, entry_id: uuid.UUID) -> bool:
            if not entry_id:
               logger.error(f"Failed to remove calendar entry: entry_id is null")
               return False
            
            query_path = self.get_graphql_path("get_calendar_rule.graphql")
            rule_response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"id": str(entry_id)},
            )
            
            try:
                rules = rule_response["data"]["calendar_event"][0]["rule"]
                rule_id = rules[0]["id"] if rules else None
            except (KeyError, IndexError):
                logger.warning(f"No rule found for calendar event {entry_id}")
                rule_id = None

            if not rule_id:
                return False

            mutation_path = self.get_graphql_path("delete_calendar_event.graphql")
            event_response = self.directus.execute_query_file(
                query_file_path=mutation_path,
                variables={
                    "eventId": str(entry_id),
                    "ruleId": str(rule_id)
                    },
            )

            if event_response.get("errors"):
                raise Exception(f"Failed to remove calendar entry: {event_response['errors']}")

            logger.info(f"Deleted calendar entry {entry_id} with rule {rule_id}")
            return True
     
   
    '''def update_calendar_entry(self, entry_id: uuid.UUID, update_data: CalendarCreate) -> list[CalendarEntry]:
            entry = await self.get_entry(user_id, entry_id)

            if not entry:
                logger.info(f"Calendar entry {entry_id} for user {user_id} not found! Creating NEW entry!!")
                return await self.create_calendar_entry(user_id, update_data) # Maybe error better to prevent duplicate entries?

            for field, value in update_data.items(): # needs update
                if field not in UPDATE_BLACKLIST:
                     setattr(entry, field, value)
                
            await self.db.commit()
            await self.db.refresh(entry)

            logger.info(f"Updated calendar entry {entry_id}")
            return self.generate_repeat_events(entry)'''

    def get_all(
        self,
        user_id: uuid.UUID,
        type: Optional[str] = None,
        frequency: Optional[str] = None,
        all_day: Optional[bool] = None
    ) -> list[CalendarEntry]:
        
        query_path = self.get_graphql_path("get_calendar_event.graphql")

        filters = {
            "user_id": {"_eq": str(user_id)}
        }

        if type:
            filters["event_type"] = {"_eq": type}
        if all_day is not None:
            filters["all_day"] = {"_eq": all_day}
        if frequency:
            filters["rule"] = {"frequency": {"_eq": frequency}}

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"filter": filters}
        )
        
        if response.get("errors"):
                raise Exception(f"Failed to get calendar entries: {response['errors']}")

        base_events = response.get("data", {}).get("calendar_event", [])

        instances = []
        for event in base_events:
            calendar_entry = CalendarEntry.from_json(event)
            instances.extend(self.generate_repeat_events(calendar_entry))

        return instances

    def generate_repeat_events(self, base_event: CalendarEntry, max_occurrences: int = REPEAT_LIMIT ) -> list[CalendarEntry]:
        rule_data = base_event.rule
        if not rule_data or rule_data.frequency == Frequency.ONCE:
            return [base_event]

        interval = rule_data.interval or 1
        repeat_end = rule_data.until_time

        def get_delta():
            match rule_data.frequency:
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

        delta = get_delta()
        if delta is None:
            return [base_event]

        instances = []
        current_start = base_event.start_time
        current_end = base_event.end_time
        count = 0

        while True:
            if repeat_end and current_start > repeat_end:
                break
            if not repeat_end and count >= max_occurrences:
                break

            instance = CalendarEntry(
                id=base_event.id,
                user_id=base_event.id,
                created_at=base_event.created_at,
                updated_at=base_event.updated_at,

                title=base_event.title,
                description=base_event.description,
                address=base_event.address,
                rule=base_event.rule,
                event_type=base_event.event_type,
                start_time=current_start,
                end_time=current_end,
                all_day=base_event.all_day
            )
            instances.append(instance)

            current_start += delta
            current_end += delta
            count += 1

        return instances