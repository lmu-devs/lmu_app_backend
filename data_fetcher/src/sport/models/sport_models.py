from datetime import datetime, time
from typing import Dict, List

from pydantic import BaseModel

from shared.src.core.logging import get_sport_fetcher_logger
from shared.src.enums.weekday_enum import WeekdayEnum
from shared.src.models import Location

logger = get_sport_fetcher_logger(__name__)


class TimeSlot(BaseModel):
    day: WeekdayEnum
    start_time: time
    end_time: time

    @classmethod
    def from_interval(cls, interval: Dict) -> List["TimeSlot"]:
        """Create TimeSlots from ZHS interval data

        Args:
            interval: Interval dict containing weekdays array and time strings
                weekdays: [0=Sunday, 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday]
                start_time: ISO datetime string (e.g., "1970-01-01T18:30:00Z")
                end_time: ISO datetime string (e.g., "1970-01-01T20:00:00Z")
        """
        slots = []

        try:
            weekdays = interval.get("weekdays", [])
            start_time_str = interval.get("start_time", "")
            end_time_str = interval.get("end_time", "")

            if not weekdays or not start_time_str or not end_time_str:
                return slots

            # Parse time from ISO datetime string
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00")).time()
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00")).time()

            # Map weekday numbers to WeekdayEnum
            # 0=Sunday, 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday
            weekday_map = {
                0: WeekdayEnum.SUNDAY,
                1: WeekdayEnum.MONDAY,
                2: WeekdayEnum.TUESDAY,
                3: WeekdayEnum.WEDNESDAY,
                4: WeekdayEnum.THURSDAY,
                5: WeekdayEnum.FRIDAY,
                6: WeekdayEnum.SATURDAY,
            }

            for weekday_num in weekdays:
                if weekday_num in weekday_map:
                    slots.append(
                        cls(
                            day=weekday_map[weekday_num],
                            start_time=start_time,
                            end_time=end_time,
                        )
                    )

        except (ValueError, KeyError) as e:
            logger.warning(f"Could not parse time slot from interval: {interval} - {str(e)}")

        return slots


class Price(BaseModel):
    student: float
    employee: float
    external: float

    @classmethod
    def from_price_options(cls, price_options: List[Dict]) -> "Price":
        """Create Price from ZHS price_options array

        Args:
            price_options: List of price dicts with 'role' and 'price' (in cents)
        """
        student_price = 0.0
        employee_price = 0.0
        external_price = 0.0

        try:
            for option in price_options:
                roles = option.get("role", [])
                price_cents = option.get("price", 0)
                price_euros = price_cents / 100.0  # Convert cents to euros

                if "Studierende" in roles:
                    student_price = price_euros
                elif "Mitarbeitende" in roles:
                    employee_price = price_euros
                elif "Kursleitung" in roles:
                    # Use Kursleitung price as external if we don't have Mitarbeitende
                    if employee_price == 0.0:
                        employee_price = price_euros
                    external_price = price_euros

            return cls(student=student_price, employee=employee_price, external=external_price)

        except (ValueError, KeyError) as e:
            logger.warning(f"Could not parse price options: {price_options} - {str(e)}")
            return cls(student=0.0, employee=0.0, external=0.0)


class TimeFrame(BaseModel):
    start_date: datetime
    end_date: datetime

    @classmethod
    def from_interval(cls, interval: Dict) -> "TimeFrame":
        """Create TimeFrame from ZHS interval data

        Args:
            interval: Interval dict containing first_date and last_date ISO strings
        """
        try:
            first_date_str = interval.get("first_date", "")
            last_date_str = interval.get("last_date", "")

            if not first_date_str or not last_date_str:
                return cls(start_date=datetime.now(), end_date=datetime.now())

            # Parse ISO datetime strings
            start_date = datetime.fromisoformat(first_date_str.replace("Z", "+00:00"))
            end_date = datetime.fromisoformat(last_date_str.replace("Z", "+00:00"))

            return cls(start_date=start_date, end_date=end_date)

        except (ValueError, KeyError) as e:
            logger.warning(f"Could not parse interval dates: {interval} - {str(e)}")
            return cls(start_date=datetime.now(), end_date=datetime.now())


class SportCourseLocation(Location):
    @classmethod
    def from_interval(cls, interval: Dict) -> "SportCourseLocation":
        """Create SportCourseLocation from ZHS interval data

        Args:
            interval: Interval dict containing locations array
        """
        try:
            locations = interval.get("locations", [])
            if not locations:
                return None

            location = locations[0]  # Use first location
            building_name = (location.get("building_name") or "").strip()
            room_name = (location.get("name") or "").strip()

            # Combine building and room name
            address = f"{building_name} - {room_name}" if building_name and room_name else (room_name or building_name)

            if not address:
                return None

            # Note: The API doesn't provide lat/long, so we set them to 0
            # These could be geocoded later if needed
            return cls(
                address=address,
                latitude=0.0,
                longitude=0.0,
            )

        except (ValueError, KeyError) as e:
            logger.warning(f"Could not parse location from interval: {interval} - {str(e)}")
            return None


class Course(BaseModel):
    id: str
    name: str
    time_slots: List[TimeSlot]
    duration: TimeFrame
    instructor: str
    price: Price
    location: SportCourseLocation | None = None
    category_id: str  # Now using offer_id as category_id
    status_code: int = 0  # No longer provided by new API
    is_available: bool = False
    total_availability: int | None = None
    today_availability: bool | None = None

    @classmethod
    def from_course_data(
        cls,
        course_data: Dict,
        offer_id: str,
        total_availability: int,
        today_availability: bool,
    ) -> "Course":
        """Create Course from ZHS course data

        Args:
            course_data: Course dict from API
            offer_id: The offer ID to use as category_id
            total_availability: Total availability from offer
            today_availability: Today availability from offer
        """
        try:
            # Extract basic info
            course_id = course_data.get("id", "")
            name = course_data.get("name", "")

            # Extract tutors/instructors
            tutors = course_data.get("tutors", [])
            instructor = ", ".join([tutor.get("name", "") for tutor in tutors])

            # Parse price
            price_options = course_data.get("price_options", [])
            price = Price.from_price_options(price_options)

            # Parse intervals (time slots, duration, location)
            intervals = course_data.get("intervals", [])
            time_slots = []
            duration = TimeFrame(start_date=datetime.now(), end_date=datetime.now())
            location = None

            if intervals:
                first_interval = intervals[0]
                time_slots = TimeSlot.from_interval(first_interval)
                duration = TimeFrame.from_interval(first_interval)
                location = SportCourseLocation.from_interval(first_interval)

            # Determine availability
            is_available = total_availability > 0 if total_availability is not None else False

            return cls(
                id=course_id,
                name=name,
                time_slots=time_slots,
                duration=duration,
                instructor=instructor,
                price=price,
                location=location,
                category_id=offer_id,
                status_code=0,
                is_available=is_available,
                total_availability=total_availability,
                today_availability=today_availability,
            )

        except Exception as e:
            logger.error(f"Error creating Course from data: {str(e)}")
            raise


class SportCourse(BaseModel):
    title: str
    courses: List[Course]

    @classmethod
    def from_offer_data(cls, offer_data: Dict, courses_data: List[Dict]) -> "SportCourse":
        """Create SportCourse from ZHS offer and courses data

        Args:
            offer_data: The offer dict containing name and availability
            courses_data: List of course dicts for this offer
        """
        title = offer_data.get("name", "Unknown Sport")
        offer_id = offer_data.get("id", "")
        total_availability = offer_data.get("total_availability")
        today_availability = offer_data.get("today_availability")

        courses = []
        for course_data in courses_data:
            try:
                course = Course.from_course_data(course_data, offer_id, total_availability, today_availability)
                courses.append(course)
            except Exception as e:
                logger.error(f"Failed to parse course {course_data.get('id')}: {str(e)}")
                continue

        return cls(title=title, courses=courses)
