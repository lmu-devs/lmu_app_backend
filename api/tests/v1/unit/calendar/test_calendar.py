from datetime import datetime, timedelta, timezone
from uuid import uuid4

from shared.src.tables import RepeatType, CalendarTable
from api.src.v1.calendar.services.calendar_service import CalendarService
from shared.src.core.logging import get_calendar_logger

logger = get_calendar_logger(__name__) #  pytest -v -o log_cli=true --log-cli-level=DEBUG api/tests/v1/unit/calendar/test_calendar.py

def test_daily_1():
    base_time = datetime.now(timezone.utc)
    base_event = CalendarTable(
        id=uuid4(),
        user_id=uuid4(),
        title="Test Event",
        description="Daily",
        event_type="SPORT",
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        repeat_type=RepeatType.DAILY,
        repeat_interval=1,
        repeat_end_time=base_time + timedelta(days=3),
        created_at=base_time,
        updated_at=base_time,
    )

    service = CalendarService(None)
    events = service.generate_repeat_events(base_event)

    assert len(events) == 4
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        assert event.start_time == base_time + timedelta(days=i)
        assert event.end_time == base_time + timedelta(days=i, hours=1)
        assert event.title == base_event.title


def test_weekly_1():
    base_time = datetime.now(timezone.utc)
    base_event = CalendarTable(
        id=uuid4(),
        user_id=uuid4(),
        title="Test Weekly",
        description=None,
        event_type="LECTURE",
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        repeat_type=RepeatType.WEEKLY,
        repeat_interval=1,
        repeat_end_time=None,
        created_at=base_time,
        updated_at=base_time,
    )

    service = CalendarService(None)
    events = service.generate_repeat_events(base_event)

    assert len(events) == 10
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        assert event.start_time == base_time + timedelta(weeks=i)

def test_weekly_2():
    base_time = datetime.now(timezone.utc)
    base_event = CalendarTable(
        id=uuid4(),
        user_id=uuid4(),
        title="Test every three weeks",
        description=None,
        event_type="LECTURE",
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        repeat_type=RepeatType.WEEKLY,
        repeat_interval=3,
        repeat_end_time=None,
        created_at=base_time,
        updated_at=base_time,
    )

    service = CalendarService(None)
    events = service.generate_repeat_events(base_event, 11)

    assert len(events) == 11
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        expected_start = base_time + timedelta(weeks=i * 3)
        assert event.start_time == expected_start
        assert event.end_time == expected_start + timedelta(hours=2)

def test_daily_2():
    base_time = datetime(2025, 6, 1, tzinfo=timezone.utc)
    base_event = CalendarTable(
        id=uuid4(),
        user_id=uuid4(),
        title="Every two days",
        description="Every two days",
        event_type="LECTURE",
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        repeat_type=RepeatType.DAILY,
        repeat_interval=2,
        repeat_end_time=base_time + timedelta(days=35),
        created_at=base_time,
        updated_at=base_time,
    )

    service = CalendarService(None)
    events = service.generate_repeat_events(base_event)

    assert len(events) == 18
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        expected_start = base_time + timedelta(days=i * 2)
        assert event.start_time == expected_start
        assert event.end_time == expected_start + timedelta(hours=1)

def test_monthly_1():
    base_time = datetime(2025, 1, 15, tzinfo=timezone.utc)
    base_event = CalendarTable(
        id=uuid4(),
        user_id=uuid4(),
        title="Monthly",
        description="Always 15.",
        event_type="LECTURE",
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        repeat_type=RepeatType.MONTHLY,
        repeat_interval=1,
        repeat_end_time=None,
        created_at=base_time,
        updated_at=base_time,
    )

    service = CalendarService(None)
    events = service.generate_repeat_events(base_event)
    assert len(events) == 10

    expected_dates = [
        datetime(2025, 1, 15, tzinfo=timezone.utc),
        datetime(2025, 2, 15, tzinfo=timezone.utc),
        datetime(2025, 3, 15, tzinfo=timezone.utc),
        datetime(2025, 4, 15, tzinfo=timezone.utc),
        datetime(2025, 5, 15, tzinfo=timezone.utc),
        datetime(2025, 6, 15, tzinfo=timezone.utc),
        datetime(2025, 7, 15, tzinfo=timezone.utc),
        datetime(2025, 8, 15, tzinfo=timezone.utc),
        datetime(2025, 9, 15, tzinfo=timezone.utc),
        datetime(2025, 10, 15, tzinfo=timezone.utc),
    ]

    for event, expected_start in zip(events, expected_dates):
        logger.debug(f"Start: {event.start_time}, End: {event.end_time}")
        assert event.start_time == expected_start
        assert event.end_time == expected_start + timedelta(hours=2)

