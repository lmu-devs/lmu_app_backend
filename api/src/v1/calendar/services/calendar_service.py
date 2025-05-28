import uuid
from typing import Optional

from api.src.v1.calendar.models.calendar_model import update_blacklist

from shared.src.core.exceptions import DatabaseError
from shared.src.core.logging import get_calendar_logger
from shared.src.tables import CalendarTable

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


    async def create_calendar_entry(self, user_id: uuid.UUID, calendar_data: dict) -> CalendarTable:
        try:
            entry = CalendarTable(
                id=uuid.uuid4(),
                user_id=user_id,
                
                title=calendar_data["title"],
                description=calendar_data.get("description"),
                event_type=calendar_data.get("event_type"),
                repeat_type=calendar_data("repeat_type"),
                start_time=calendar_data.get("start_time"),
                end_time=calendar_data.get("end_time"),
            )

            self.db.add(entry)
            await self.db.commit()

            logger.info( f"Created new calendar entry for user {user_id}")

            return entry

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
        

    async def update_calendar_entry(self, user_id: uuid.UUID, entry_id: uuid.UUID, update_data: dict) -> CalendarTable:
        try:
            entry = await self.get_entry(user_id, entry_id)

            if not entry:
                logger.info(f"Calendar entry {entry_id} for user {user_id} not found! Creating NEW entry!!")
                return self.create_calendar_entry(user_id, update_data) # Maybe error better to prevent duplicate entries?

            for field, value in update_data.items():
                if field not in update_blacklist:
                     setattr(entry, field, value)
                
            await self.db.commit()
            await self.db.refresh(entry)

            logger.info(f"Updated calendar entry {entry_id} for user {user_id}")
            return entry

        except SQLAlchemyError as e:
            logger.error(f"Failed to update calendar entry: {str(e)}")
            await self.db.rollback()
            raise DatabaseError(detail="Failed to update calendar entry", extra={"original_error": str(e)})
        

    async def get_all( # TODO: Implement router, Implement daily, weekly, etc -> set max limit for one event
        self,
        user_id: uuid.UUID,
        event_type: Optional[str] = None,
        repeat_type: Optional[str] = None
    ) -> list[CalendarTable]:
            stmt = select(CalendarTable).where(CalendarTable.user_id == user_id)

            if event_type:
                stmt = stmt.where(CalendarTable.event_type == event_type)
            if repeat_type:
                stmt = stmt.where(CalendarTable.repeat_type == repeat_type)

            result = await self.db.execute(stmt)
            return result.scalars().all()