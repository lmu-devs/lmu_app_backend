

from pydantic import BaseModel
from datetime import date, datetime, time
from typing import List

from shared.src.enums import WeekdayEnum
from shared.src.models import Location

class TimeSlot(BaseModel):
    day: WeekdayEnum
    start_time: time
    end_time: time

class Price(BaseModel):
    student_price: float
    employee_price: float
    external_price: float

class SportCourse(BaseModel):
    title: str
    is_available: bool
    start_date: datetime
    end_date: datetime
    instructor: str
    time_slots: List[TimeSlot]
    price: Price
    location: Location | None = None
    
    
class SportType(BaseModel):
    title: str
    courses: List[SportCourse]


    
