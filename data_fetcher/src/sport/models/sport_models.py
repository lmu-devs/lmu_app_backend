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
    def from_pattern(cls, day_patterns: List[int], time_patterns: List[str], tage_data: List[List[int]]) -> List['TimeSlot']:
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
            if not time_str or time_str == '--':
                continue
                
            try:
                # Parse the time string
                start, end = time_str.split('-')
                
                # Parse start time
                start = start.strip()
                if ':' in start:
                    start_time = datetime.strptime(start, '%H:%M').time()
                else:
                    start_time = datetime.strptime(start, '%H.%M').time()
                
                # Parse end time
                end = end.strip()
                if ':' in end:
                    end_time = datetime.strptime(end, '%H:%M').time()
                else:
                    end_time = datetime.strptime(end, '%H.%M').time()
                
                # Create a TimeSlot for each active day in the pattern
                for day_idx, is_active in enumerate(weekday_pattern):
                    if is_active:
                        slots.append(cls(
                            day=WeekdayEnum[list(WeekdayEnum)[day_idx].name],
                            start_time=start_time,
                            end_time=end_time
                        ))
                        
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse time slot for pattern {pattern_idx}: {time_patterns} - {str(e)}")
                continue
                
        return slots

class Price(BaseModel):
    student: float
    employee: float
    external: float

    @classmethod
    def from_price_string(cls, price: str) -> 'Price':
        """Create Price from ZHS price string"""
        # Handle special cases
        if not price or 'nur mit' in price or 'entgeltfrei' in price:
            return cls(student=0.0, employee=0.0, external=0.0)
            
        try:
            # Remove HTML and euro symbol
            price = price.replace('€', '').strip()
            if price == '--':
                return cls(student=0.0, employee=0.0, external=0.0)
                
            # Split and parse prices
            prices = price.split('/')
            
            # Convert prices, handling both . and , as decimal separator
            # and handling '--' as 0.0
            def parse_price(p: str) -> float:
                p = p.strip()
                return 0.0 if p == '--' else float(p.replace(',', '.'))
                
            return cls(
                student=parse_price(prices[0]),
                employee=parse_price(prices[1]) if len(prices) > 1 else 0.0,
                external=parse_price(prices[2]) if len(prices) > 2 else 0.0
            )
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse price: {price} - {str(e)}")
            return cls(student=0.0, employee=0.0, external=0.0)

class TimeFrame(BaseModel):
    start_date: datetime
    end_date: datetime

    @classmethod
    def from_duration_string(cls, duration: str) -> 'TimeFrame':
        """Create TimeFrame from ZHS duration string"""
        try:
            if not duration or duration == '--' or duration == '???':
                # Return a default timeframe if no duration is specified
                return cls(
                    start_date=datetime.now(),
                    end_date=datetime.now()
                )
                
            # Handle single date case (e.g., "25.01.2025")
            if duration.count('-') == 0:
                date = datetime.strptime(duration.strip(), '%d.%m.%Y')
                return cls(
                    start_date=date,
                    end_date=date
                )
                
            # Handle normal range case (e.g., "14.10.2024-08.02.2025")
            start, end = duration.split('-')
            return cls(
                start_date=datetime.strptime(start.strip(), '%d.%m.%Y'),
                end_date=datetime.strptime(end.strip(), '%d.%m.%Y')
            )
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse duration: {duration} - {str(e)}")
            return cls(
                start_date=datetime.now(),
                end_date=datetime.now()
            )
            

class SportCourseLocation(Location):
    
    @classmethod
    def from_pattern(cls, location_data: list[str, float, float]) -> 'SportCourseLocation':
        if not location_data or len(location_data) < 3:
            return None
        # Skip if any required field is empty or invalid
        if not location_data[0] or not location_data[1] or not location_data[2]:
            return None
        return cls(
            address=location_data[0],
            latitude=location_data[1],
            longitude=location_data[2]
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
    def from_course_list(cls, courses: List[Course]) -> List['SportCourse']:
        """Group courses by their title"""
        course_dict: Dict[str, List[Course]] = {}
        
        for course in courses:
            if course.title not in course_dict:
                course_dict[course.title] = []
            course_dict[course.title].append(course)
        
        return [
            cls(title=title, courses=course_list)
            for title, course_list in course_dict.items()
        ]
        
