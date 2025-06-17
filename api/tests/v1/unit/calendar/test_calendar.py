from datetime import datetime, timedelta, timezone
from uuid import uuid4

from api.src.v1.calendar.models.calendar_model import CalendarEntry, CalendarRule, Frequency
from api.src.v1.calendar.services.calendar_service import CalendarService
from shared.src.core.logging import get_calendar_logger

logger = get_calendar_logger(__name__) #  pytest -v -o log_cli=true --log-cli-level=DEBUG api/tests/v1/unit/calendar/test_calendar.py

def test_daily_1():
    base_time = datetime.now(timezone.utc)
    base_event = CalendarEntry(
        title="Test Event",
        description="Daily",
        address=None,
        rule=CalendarRule(
            frequency=Frequency.DAILY,
            interval=1,
            until_time=base_time + timedelta(days=3),
        ),
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        event_type="SPORT",
        all_day=False,
        id=uuid4(),
        user_id=uuid4(),
        created_at=base_time,
        updated_at=base_time,
    )
    events = CalendarService().generate_repeat_events(base_event)

    assert len(events) == 4
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        assert event.start_time == base_time + timedelta(days=i)
        assert event.end_time == base_time + timedelta(days=i, hours=1)
        assert event.title == base_event.title

def test_weekly_1():
    base_time = datetime.now(timezone.utc)
    base_event = CalendarEntry(
        title="Test Weekly",
        description=None,
        address=None,
        rule=CalendarRule(
            frequency=Frequency.WEEKLY,
            interval=1,
            until_time=base_time + timedelta(weeks=9),
        ),
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        event_type="LECTURE",
        all_day=False,
        id=uuid4(),
        user_id=uuid4(),
        created_at=base_time,
        updated_at=base_time,
    )

    events = CalendarService().generate_repeat_events(base_event)

    assert len(events) == 10
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        assert event.start_time == base_time + timedelta(weeks=i)

def test_weekly_2():
    base_time = datetime.now(timezone.utc)
    base_event = CalendarEntry(
        title="Test every three weeks",
        description=None,
        address=None,
        rule=CalendarRule(
            frequency=Frequency.WEEKLY,
            interval=3,
            until_time=base_time + timedelta(weeks=30),
        ),
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        event_type="LECTURE",
        all_day=False,
        id=uuid4(),
        user_id=uuid4(),
        created_at=base_time,
        updated_at=base_time,
    )

    events = CalendarService().generate_repeat_events(base_event)

    assert len(events) == 11
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        expected_start = base_time + timedelta(weeks=i * 3)
        assert event.start_time == expected_start
        assert event.end_time == expected_start + timedelta(hours=2)

def test_daily_2():
    base_time = datetime(2025, 6, 1, tzinfo=timezone.utc)
    base_event = CalendarEntry(
        title="Every two days",
        description="Every two days",
        address=None,
        rule=CalendarRule(
            frequency=Frequency.DAILY,
            interval=2,
            until_time=base_time + timedelta(days=34),
        ),
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        event_type="LECTURE",
        all_day=False,
        id=uuid4(),
        user_id=uuid4(),
        created_at=base_time,
        updated_at=base_time,
    )

    events = CalendarService().generate_repeat_events(base_event)

    assert len(events) == 18
    for i, event in enumerate(events):
        logger.debug(f"[{i}] Start: {event.start_time}, End: {event.end_time}")
        expected_start = base_time + timedelta(days=i * 2)
        assert event.start_time == expected_start
        assert event.end_time == expected_start + timedelta(hours=1)

def test_monthly_1():
    base_time = datetime(2025, 1, 15, tzinfo=timezone.utc)
    base_event = CalendarEntry(
        title="Monthly",
        description="Always 15.",
        address=None,
        rule=CalendarRule(
            frequency=Frequency.MONTHLY,
            interval=1,
            until_time=datetime(2025, 10, 15, tzinfo=timezone.utc),
        ),
        start_time=base_time,
        end_time=base_time + timedelta(hours=2),
        event_type="LECTURE",
        all_day=False,
        id=uuid4(),
        user_id=uuid4(),
        created_at=base_time,
        updated_at=base_time,
    )

    events = CalendarService().generate_repeat_events(base_event)
    assert len(events) == 10

    expected_dates = [
        datetime(2025, month, 15, tzinfo=timezone.utc) for month in range(1, 11)
    ]

    for event, expected_start in zip(events, expected_dates):
        logger.debug(f"Start: {event.start_time}, End: {event.end_time}")
        assert event.start_time == expected_start
        assert event.end_time == expected_start + timedelta(hours=2)

def test_yearly_1():
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    base_event = CalendarEntry(
        title="1st",
        description="on Jan 1st",
        address=None,
        rule=CalendarRule(
            frequency=Frequency.YEARLY,
            interval=1,
            until_time=datetime(2034, 1, 1, tzinfo=timezone.utc),
        ),
        start_time=base_time,
        end_time=base_time + timedelta(hours=3),
        event_type="LECTURE",
        all_day=False,
        id=uuid4(),
        user_id=uuid4(),
        created_at=base_time,
        updated_at=base_time,
    )

    events = CalendarService().generate_repeat_events(base_event)

    assert len(events) == 10

    expected_dates = [
        datetime(year, 1, 1, tzinfo=timezone.utc)
        for year in range(2025, 2025 + 10)
    ]

    for event, expected_start in zip(events, expected_dates):
        logger.debug(f"Start: {event.start_time}, End: {event.end_time}")
        assert event.start_time == expected_start
        assert event.end_time == expected_start + timedelta(hours=3)