from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.timeline_model import Timeline
from ..models.event_model import Event, EventTypeEnum
from ..models.semester_model import SemesterTypeEnum, Semester
from shared.src.models import Timeframe


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
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2024, 10, 15), end=datetime(2024, 10, 15)),
                ),
                Event(
                title="Winterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2024, 12, 24), end=datetime(2025, 1, 6)),
                ),
                Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2024, 12, 1), end=datetime(2025, 2, 8)),
                ),
                Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 2, 8), end=datetime(2025, 4, 21)),
                ),
                # Sommer
                Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 4, 22), end=datetime(2025, 4, 22)),
                ),
                Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 7, 26), end=datetime(2025, 10, 12)),
                ),
                # Winter
                Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 10, 13), end=datetime(2025, 10, 13)),
                ),
                Event(
                title="Winterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 12, 24), end=datetime(2026, 1, 6)),
                ),
                Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 12, 1), end=datetime(2026, 2, 8)),
                ),
                # Sommer
                Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 4, 13), end=datetime(2026, 4, 13)),
                ),
                Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 7, 17), end=datetime(2027, 10, 11)),
                ),
                # Winter
                Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 10, 13), end=datetime(2026, 10, 13)),
                ),
                Event(
                title="Winterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 12, 13), end=datetime(2027, 1, 13)),
                ),
                Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 12, 15), end=datetime(2027, 2, 8)),
                ),
                Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 2, 6), end=datetime(2027, 4, 12)),
                ),
                # Sommer
                Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 4, 12), end=datetime(2027, 4, 12)),
                ),
                Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 7, 25), end=datetime(2027, 10, 10)),
                ),
            ]
    
    def get_semesters(self) -> List[Semester]:
        # Mock semesters
        return [
                Semester(timeframe=Timeframe(start=datetime(2024, 10, 1), end=datetime(2025, 3, 31)), type=SemesterTypeEnum.WINTER),
                Semester(timeframe=Timeframe(start=datetime(2025, 4, 1), end=datetime(2025, 9, 30)), type=SemesterTypeEnum.SUMMER),
                Semester(timeframe=Timeframe(start=datetime(2025, 10, 1), end=datetime(2026, 3, 31)), type=SemesterTypeEnum.WINTER),
                Semester(timeframe=Timeframe(start=datetime(2026, 4, 1), end=datetime(2026, 9, 30)), type=SemesterTypeEnum.SUMMER),
                Semester(timeframe=Timeframe(start=datetime(2026, 10, 1), end=datetime(2027, 3, 31)), type=SemesterTypeEnum.WINTER),
                Semester(timeframe=Timeframe(start=datetime(2027, 4, 1), end=datetime(2027, 9, 30)), type=SemesterTypeEnum.SUMMER),
                Semester(timeframe=Timeframe(start=datetime(2027, 10, 1), end=datetime(2028, 3, 31)), type=SemesterTypeEnum.WINTER),
            ]
        