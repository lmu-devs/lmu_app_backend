from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.timeline_model import Timeline
from ..models.event_model import Event, EventTypeEnum
from ..models.semester_model import SemesterTypeEnum, Semester
from shared.src.models import Timeframe, Location


class TimelineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_timeline(self) -> Timeline:
        # Mock timeline
        return Timeline(
            events=self.get_events(),
            semesters=self.get_semesters(),
        )

    def get_events(self) -> List[Event]:
        # Mock events
        return [
                Event(
                title="Semester start",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2024, 10, 1), end=datetime(2024, 12, 23)),
                ),
                Event(
                title="Weihnachtsferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2024, 12, 24), end=datetime(2025, 1, 6)),
                ),
                Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2024, 12, 1), end=datetime(2025, 2, 8)),
                ),
                Event(
                title="Vorlesungszeit",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 1, 7), end=datetime(2025, 2, 8)),
                ),
                Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 2, 15), end=datetime(2025, 4, 21)),
                ),
                Event(
                title="Semesterstart",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 4, 22), end=datetime(2025, 7, 1)),
                ),
            ]
    
    def get_semesters(self) -> List[Semester]:
        # Mock semesters
        return [
                Semester(timeframe=Timeframe(start=datetime(2024, 10, 1), end=datetime(2025, 2, 1)), type=SemesterTypeEnum.WINTER),
                Semester(timeframe=Timeframe(start=datetime(2025, 4, 1), end=datetime(2025, 7, 1)), type=SemesterTypeEnum.SUMMER),
                Semester(timeframe=Timeframe(start=datetime(2025, 10, 1), end=datetime(2026, 1, 1)), type=SemesterTypeEnum.WINTER),
            ]
        