from datetime import datetime, time
from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums import WeekdayEnum
from shared.src.models import Location
from shared.src.tables.sport.sport_table import SportCourseTable, SportCourseTimeSlotTable, SportTypeTable


class TimeSlot(BaseModel):
    day: WeekdayEnum
    start_time: time
    end_time: time
    
    @classmethod
    def from_table(cls, table: SportCourseTimeSlotTable) -> "TimeSlot":
        return cls(
            day=table.day,
            start_time=table.start_time,
            end_time=table.end_time
        )
        
class TimeSlots(RootModel):
    root: List[TimeSlot]
    
    @classmethod
    def from_table(cls, tables: List[SportCourseTimeSlotTable]) -> "TimeSlots":
        return cls(root=[TimeSlot.from_table(table) for table in tables])

class Price(BaseModel):
    student_price: float
    employee_price: float
    external_price: float

class SportCourse(BaseModel):
    id: str
    title: str
    is_available: bool
    start_date: datetime
    end_date: datetime
    instructor: str
    time_slots: TimeSlots
    price: Price
    location: Location | None = None
    
    @classmethod
    def from_table(cls, table: SportCourseTable) -> "SportCourse":
        title = table.translations[0].title if table.translations else "not translated"
        
        price = Price(
            student_price=table.student_price,
            employee_price=table.employee_price,
            external_price=table.external_price
        )
        
        location = None
        if table.location:
            location = Location.from_table(table.location)
        
        timeslots = TimeSlots.from_table(table.time_slots)
        
        return SportCourse(   
            id=table.id,
            title=title,
            is_available=table.is_available,
            start_date=table.start_date,
            end_date=table.end_date,
            instructor=table.instructor,
            time_slots=timeslots,
            price=price,
            location=location
        )
        
class SportCourses(RootModel):
    root: List[SportCourse]
    
    @classmethod
    def from_table(cls, tables: List[SportCourseTable]) -> "SportCourses":
        return cls(root=[SportCourse.from_table(table) for table in tables])
    
class SportType(BaseModel):
    title: str
    courses: SportCourses
    
    @classmethod
    def from_table(cls, table: SportTypeTable) -> "SportType":
        return cls(
            title=table.translations[0].title if table.translations else "not translated",
            courses=SportCourses.from_table(table.sport_courses)
        )
        
class SportTypes(RootModel):
    root: List[SportType]
    
    @classmethod
    def from_table(cls, tables: List[SportTypeTable]) -> "SportTypes":
        return cls(root=[SportType.from_table(table) for table in tables])
    
    
class Sport(BaseModel):
    base_url: str
    basic_ticket: SportType
    sport_types: SportTypes
    
    @classmethod
    def model(cls, sport_types: SportTypes, basic_ticket: SportType) -> "Sport":
        return cls(
            base_url="https://www.buchung.zhs-muenchen.de/angebote/aktueller_zeitraum_0/",
            basic_ticket=basic_ticket,
            sport_types=sport_types
        )


    
