from datetime import datetime, time
from typing import Dict, List

from pydantic import BaseModel, Field

from shared.src.core.logging import get_sport_fetcher_logger
from shared.src.enums.weekday_enum import WeekdayEnum
from shared.src.models import Location

logger = get_sport_fetcher_logger(__name__)


class TimeSlot(BaseModel):
    day: WeekdayEnum
    start_time: time
    end_time: time

    @classmethod
    def from_pattern(
        cls,
        day_patterns: List[int],
        time_patterns: List[str],
        tage_data: List[List[int]],
    ) -> List["TimeSlot"]:
        """Create TimeSlots from the ZHS day and time patterns

        Args:
            day_patterns: List where numbers reference indices in tage_data
            time_patterns: List of time strings in format "HH:MM-HH:MM" or "HH.MM-HH.MM"
            tage_data: List of day patterns from ZHS data where each pattern is [Mo,Di,Mi,Do,Fr,Sa,So]
        """
        slots = []

        for pattern_idx in day_patterns:
            if pattern_idx <= 0 or pattern_idx >= len(tage_data):
                continue

            # Get the weekday pattern (array of 7 integers where 1 indicates active day)
            weekday_pattern = tage_data[pattern_idx][1:]  # Skip first element (name)

            # Get the corresponding time pattern
            time_str = time_patterns[0].strip()  # Default to first time pattern
            if not time_str or time_str == "--":
                continue

            try:
                # Parse the time string
                start, end = time_str.split("-")

                # Parse start time
                start = start.strip()
                if ":" in start:
                    start_time = datetime.strptime(start, "%H:%M").time()
                else:
                    start_time = datetime.strptime(start, "%H.%M").time()

                # Parse end time
                end = end.strip()
                if ":" in end:
                    end_time = datetime.strptime(end, "%H:%M").time()
                else:
                    end_time = datetime.strptime(end, "%H.%M").time()

                # Create a TimeSlot for each active day in the pattern
                for day_idx, is_active in enumerate(weekday_pattern):
                    if is_active:
                        slots.append(
                            cls(
                                day=WeekdayEnum[list(WeekdayEnum)[day_idx].name],
                                start_time=start_time,
                                end_time=end_time,
                            )
                        )

            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse time slot for pattern {pattern_idx}: {time_patterns} - {str(e)}")
                continue

        return slots


class Price(BaseModel):
    student: float
    employee: float
    external: float

    @classmethod
    def from_price_string(cls, price: str) -> "Price":
        """Create Price from ZHS price string"""
        # Handle special cases
        if not price or "nur mit" in price or "entgeltfrei" in price:
            return cls(student=0.0, employee=0.0, external=0.0)

        try:
            # Remove HTML and euro symbol
            price = price.replace("€", "").strip()
            if price == "--":
                return cls(student=0.0, employee=0.0, external=0.0)

            # Split and parse prices
            prices = price.split("/")

            # Convert prices, handling both . and , as decimal separator
            # and handling '--' as 0.0
            def parse_price(p: str) -> float:
                p = p.strip()
                return 0.0 if p == "--" else float(p.replace(",", "."))

            return cls(
                student=parse_price(prices[0]),
                employee=parse_price(prices[1]) if len(prices) > 1 else 0.0,
                external=parse_price(prices[2]) if len(prices) > 2 else 0.0,
            )
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse price: {price} - {str(e)}")
            return cls(student=0.0, employee=0.0, external=0.0)


class TimeFrame(BaseModel):
    start_date: datetime
    end_date: datetime

    @classmethod
    def from_duration_string(cls, duration: str) -> "TimeFrame":
        """Create TimeFrame from ZHS duration string

        Handles various formats:
        - Single date with year: '30.05.25'
        - Single date without year: '30.05.'
        - Date range with year: '31.05.-01.06.25'
        - Multiple dates: '23.04., 28.04., 30.04., 05.05.'
        - Multiple date ranges: '17.05.-18.05./24.05.-25.05.25'
        """
        try:
            if not duration or duration == "--" or duration == "???":
                return cls(start_date=datetime.now(), end_date=datetime.now())

            # Clean up the input string
            duration = duration.strip()

            # Helper function to parse date with flexible year
            def parse_date(date_str: str, year: str = None) -> datetime:
                date_str = date_str.strip()
                if date_str.endswith("."):
                    date_str = date_str[:-1]  # Remove trailing dot

                # Split into components
                parts = date_str.split(".")
                if len(parts) < 2:
                    raise ValueError(f"Invalid date format: {date_str}")

                day = int(parts[0])
                month = int(parts[1])

                # Handle year
                if len(parts) > 2:
                    year = parts[2]
                if year:
                    if len(year) == 2:
                        year = f"20{year}"  # Assume 20xx for 2-digit years
                else:
                    year = str(datetime.now().year)

                return datetime(int(year), month, day)

            # Case 1: Multiple date ranges with slashes
            if "/" in duration:
                ranges = duration.split("/")
                dates = []
                year = None
                # Extract year from the last range if present
                if ranges[-1].strip().split(".")[-1].isdigit():
                    year = ranges[-1].strip().split(".")[-1]

                for date_range in ranges:
                    if "-" in date_range:
                        start, end = date_range.split("-")
                        dates.extend([parse_date(start, year), parse_date(end, year)])
                    else:
                        dates.append(parse_date(date_range, year))

                return cls(start_date=min(dates), end_date=max(dates))

            # Case 2: Multiple dates with commas
            if "," in duration:
                dates = []
                parts = duration.split(",")
                year = None
                # Extract year from the last part if present
                if parts[-1].strip().split(".")[-1].isdigit():
                    year = parts[-1].strip().split(".")[-1]

                for part in parts:
                    dates.append(parse_date(part, year))

                return cls(start_date=min(dates), end_date=max(dates))

            # Case 3: Single date range
            if "-" in duration:
                start, end = duration.split("-")
                year = None
                # Extract year from end date if present
                if end.strip().split(".")[-1].isdigit():
                    year = end.strip().split(".")[-1]

                return cls(start_date=parse_date(start, year), end_date=parse_date(end, year))

            # Case 4: Single date
            return cls(start_date=parse_date(duration), end_date=parse_date(duration))

        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse duration: {duration} - {str(e)}")
            return cls(start_date=datetime.now(), end_date=datetime.now())


class SportCourseLocation(Location):
    @classmethod
    def from_pattern(cls, location_data: list[str, float, float]) -> "SportCourseLocation":
        if not location_data or len(location_data) < 3:
            return None
        # Skip if any required field is empty or invalid
        if not location_data[0] or not location_data[1] or not location_data[2]:
            return None
        return cls(
            address=location_data[0],
            latitude=location_data[1],
            longitude=location_data[2],
        )


class Course(BaseModel):
    id: str
    name: str
    time_slots: List[TimeSlot]
    duration: TimeFrame
    instructor: str
    price: Price
    location: SportCourseLocation | None = None
    category_id: int
    status_code: int = Field(..., description="Usually 5, meaning might be related to course status")
    is_available: bool = False


class SportCourse(BaseModel):
    title: str
    courses: List[Course]

    @classmethod
    def from_course_list(cls, courses: List[Course]) -> List["SportCourse"]:
        """Group courses by their title"""
        course_dict: Dict[str, List[Course]] = {}

        for course in courses:
            if course.title not in course_dict:
                course_dict[course.title] = []
            course_dict[course.title].append(course)

        return [cls(title=title, courses=course_list) for title, course_list in course_dict.items()]
