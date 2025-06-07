import uuid
from typing import Optional
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from api.src.v1.calendar.models.calendar_model import UPDATE_BLACKLIST, REPEAT_LIMIT

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_calendar_logger
from shared.src.tables import CalendarTable, RepeatType

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_calendar_logger(__name__)


class CalendarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_entry(self, user_id: uuid.UUID, entry_id: uuid.UUID) -> (CalendarTable | None):
        try:
            stmt = select(CalendarTable).where(
                CalendarTable.id == entry_id,
                CalendarTable.user_id == user_id
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to get calendar entry: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(detail="Failed to get calendar entry", extra={"original_error": str(e)})


    async def create_calendar_entry(self, user_id: uuid.UUID, calendar_data: dict) -> list[CalendarTable]:
        try:
            entry = CalendarTable(
                id=uuid.uuid4(),
                user_id=user_id,
                title=calendar_data["title"],
                description=calendar_data.get("description"),
                event_type=calendar_data["event_type"],
                start_time=calendar_data["start_time"],
                end_time=calendar_data["end_time"],
                all_day=calendar_data["all_day"],
                repeat_type=calendar_data["repeat_type"],
                repeat_interval=calendar_data.get("repeat_interval"),
                repeat_end_time=calendar_data.get("repeat_end_time")
            )

            self.db.add(entry)
            await self.db.commit()

            logger.info( f"Created new calendar entry for user {user_id}")

            return self.generate_repeat_events(entry)

        except SQLAlchemyError as e:
            logger.error(f"Failed to create calendar entry: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(detail="Failed to create calendar entry", extra={"original_error": str(e)})
        

    async def remove_calendar_entry(self, user_id: uuid.UUID, entry_id: uuid.UUID) -> bool:
        try:
            entry = await self.get_entry(user_id, entry_id)

            if not entry:
                logger.info(f"Calendar entry {entry_id} for user {user_id} not found!")
                return False

            await self.db.delete(entry)
            await self.db.commit()

            logger.info(f"Deleted calendar entry {entry_id} for user {user_id}")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to delete calendar entry: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(detail="Failed to delete calendar entry", extra={"original_error": str(e)})
        

    async def update_calendar_entry(self, user_id: uuid.UUID, entry_id: uuid.UUID, update_data: dict) -> list[CalendarTable]:
        try:
            entry = await self.get_entry(user_id, entry_id)

            if not entry:
                logger.info(f"Calendar entry {entry_id} for user {user_id} not found! Creating NEW entry!!")
                return await self.create_calendar_entry(user_id, update_data) # Maybe error better to prevent duplicate entries?

            for field, value in update_data.items():
                if field not in UPDATE_BLACKLIST:
                     setattr(entry, field, value)
                
            await self.db.commit()
            await self.db.refresh(entry)

            logger.info(f"Updated calendar entry {entry_id} for user {user_id}")
            return self.generate_repeat_events(entry)

        except SQLAlchemyError as e:
            logger.error(f"Failed to update calendar entry: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(detail="Failed to update calendar entry", extra={"original_error": str(e)})
        
    async def get_all(
        self,
        user_id: uuid.UUID,
        event_type: Optional[str] = None,
        repeat_type: Optional[str] = None,
        all_day: Optional[bool] = None
    ) -> list[CalendarTable]:
            stmt = select(CalendarTable).where(CalendarTable.user_id == user_id)

            if all_day is not None:
                stmt = stmt.where(CalendarTable.all_day == all_day)
            if event_type:
                stmt = stmt.where(CalendarTable.event_type == event_type)
            if repeat_type:
                stmt = stmt.where(CalendarTable.repeat_type == repeat_type)

            result = await self.db.execute(stmt)
            return result.scalars().all()

    def generate_repeat_events(
        self,
        base_event: CalendarTable,
        max_occurrences: int = REPEAT_LIMIT
    ) -> list[CalendarTable]:
        
        if not base_event.repeat_type or base_event.repeat_type == RepeatType.ONCE:
            return [base_event]

        interval = base_event.repeat_interval or 1
        repeat_end = base_event.repeat_end_time

        def get_delta():
            match base_event.repeat_type:
                case RepeatType.DAILY:
                    return timedelta(days=interval)
                case RepeatType.WEEKLY:
                    return timedelta(weeks=interval)
                case RepeatType.MONTHLY:
                    return relativedelta(months=interval)
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

            instance = CalendarTable(
                id=base_event.id,  # same ID, allows removing all generated events
                user_id=base_event.user_id,
                title=base_event.title,
                description=base_event.description,
                event_type=base_event.event_type,
                repeat_type=base_event.repeat_type,
                repeat_interval=base_event.repeat_interval,
                repeat_end_time=base_event.repeat_end_time,
                start_time=current_start,
                end_time=current_end,
                all_day=base_event.all_day,
                created_at=base_event.created_at,
                updated_at=base_event.updated_at
            )
            instances.append(instance)

            current_start += delta
            current_end += delta
            count += 1

        return instances

    async def get_all_with_repeats(
        self,
        user_id: uuid.UUID,
        event_type: Optional[str] = None,
        repeat_type: Optional[str] = None,
        all_day: Optional[bool] = None
    ) -> list[CalendarTable]:
        
            base_events = await self.get_all(user_id, event_type, repeat_type, all_day)
            instances = []

            for event in base_events:
                instances.extend(self.generate_repeat_events(event))

            return instances