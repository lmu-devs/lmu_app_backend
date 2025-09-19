from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.models import Timeframe

from ..models.event_model import Event, EventTypeEnum
from ..models.semester_model import Semester, SemesterTypeEnum
from ..models.timeline_model import Timeline


# TODO: Localize the timeline data
class TimelineService:
    """
    Service to load the timeline data (from the database).
    """

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
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 7, 26), end=datetime(2025, 10, 12)),
            ),
            Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2025, 7, 26), end=datetime(2025, 10, 12)),
            ),
            # Winter 2025/26
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
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 2, 7), end=datetime(2026, 4, 12)),
            ),
            Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 2, 7), end=datetime(2026, 4, 12)),
            ),
            # Summer 2026
            Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 4, 13), end=datetime(2026, 4, 13)),
            ),
            Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 7, 18), end=datetime(2026, 10, 11)),
            ),
            Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 7, 18), end=datetime(2026, 10, 11)),
            ),
            # Winter 2026/27
            Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 10, 12), end=datetime(2026, 10, 12)),
            ),
            Event(
                title="Winterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2026, 12, 24), end=datetime(2027, 1, 6)),
            ),
            Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 2, 6), end=datetime(2027, 4, 11)),
            ),
            Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 2, 6), end=datetime(2027, 4, 11)),
            ),
            # Summer 2027
            Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 4, 12), end=datetime(2027, 4, 12)),
            ),
            Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 7, 17), end=datetime(2027, 10, 17)),
            ),
            Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 7, 17), end=datetime(2027, 10, 17)),
            ),
            # Winter 2027/28
            Event(
                title="Vorlesungsbeginn",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 10, 18), end=datetime(2027, 10, 18)),
            ),
            Event(
                title="Winterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2027, 12, 24), end=datetime(2028, 1, 6)),
            ),
            Event(
                title="Semesterferien",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2028, 2, 12), end=datetime(2028, 4, 9)),
            ),
            Event(
                title="Semesterbeitrag zahlen",
                type=EventTypeEnum.SEMESTER,
                timeframe=Timeframe(start=datetime(2028, 2, 12), end=datetime(2028, 4, 9)),
            ),
        ]

    def get_semesters(self) -> List[Semester]:
        # Mock semesters
        return [
            Semester(
                timeframe=Timeframe(start=datetime(2025, 4, 1), end=datetime(2025, 9, 30)),
                type=SemesterTypeEnum.SUMMER,
            ),
            Semester(
                timeframe=Timeframe(start=datetime(2025, 10, 1), end=datetime(2026, 3, 31)),
                type=SemesterTypeEnum.WINTER,
            ),
            Semester(
                timeframe=Timeframe(start=datetime(2026, 4, 1), end=datetime(2026, 9, 30)),
                type=SemesterTypeEnum.SUMMER,
            ),
            Semester(
                timeframe=Timeframe(start=datetime(2026, 10, 1), end=datetime(2027, 3, 31)),
                type=SemesterTypeEnum.WINTER,
            ),
            Semester(
                timeframe=Timeframe(start=datetime(2027, 4, 1), end=datetime(2027, 9, 30)),
                type=SemesterTypeEnum.SUMMER,
            ),
            Semester(
                timeframe=Timeframe(start=datetime(2027, 10, 1), end=datetime(2028, 3, 31)),
                type=SemesterTypeEnum.WINTER,
            ),
        ]
