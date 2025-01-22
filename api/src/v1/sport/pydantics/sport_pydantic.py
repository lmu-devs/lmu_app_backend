from typing import List
from api.src.v1.sport.schemas.sport_schema import Price, SportCourse, SportType, TimeSlot
from shared.src.schemas import Location
from shared.src.tables.sport import SportCourseTable, SportTypeTable, SportCourseTimeSlotTable


async def sport_types_to_pydantic(sports: List[SportTypeTable]) -> List[SportType]:
    return [await sport_type_to_pydantic(sport) for sport in sports]

async def sport_type_to_pydantic(sport_type: SportTypeTable) -> SportType:
    title = sport_type.translations[0].title if sport_type.translations else "not translated"
    return SportType(
        title=title,
        courses=[await course_to_pydantic(course) for course in sport_type.sport_courses]
    )
    
    
async def courses_to_pydantic(courses: List[SportCourseTable]) -> List[SportCourse]:
    return [await course_to_pydantic(course) for course in courses]

async def course_to_pydantic(course: SportCourseTable) -> SportCourse:
    title = course.translations[0].title if course.translations else "not translated"
    
    price = Price(
        student_price=course.student_price,
        employee_price=course.employee_price,
        external_price=course.external_price
    )
    
    location = Location(
        address=str(course.location_code),
        latitude=course.location_code,
        longitude=course.location_code
    )
    
    timeslots = await timeslots_to_pydantic(course.time_slots)
    
    return SportCourse(
        title=title,
        is_available=course.is_available,
        start_date=course.start_date,
        end_date=course.end_date,
        instructor=course.instructor,
        time_slots=timeslots,
        price=price,
        location=location
    )


async def timeslots_to_pydantic(timeslots: SportCourseTimeSlotTable) -> List[TimeSlot]:
    return [await time_slot_to_pydantic(time_slot) for time_slot in timeslots]

async def time_slot_to_pydantic(timeslot: SportCourseTimeSlotTable) -> TimeSlot:
    return TimeSlot(
        day=timeslot.day,
        start_time=timeslot.start_time,
        end_time=timeslot.end_time
    )