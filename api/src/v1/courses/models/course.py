from datetime import date as Date
from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel

from shared.src.enums.courses_enums import CourseStartTypeEnum
from shared.src.enums.weekday_enum import WeekdayEnum


class Person(BaseModel):
    first_name: str
    surname: str
    title: Optional[str]


class Institution(BaseModel):
    name: str


class PathElement(BaseModel):
    value: str
    index: int


class TreePath(BaseModel):
    path_elements: List[PathElement]


class AssociatedProgram(BaseModel):
    program_name: Optional[str]
    module_classification: Optional[str]
    ects: Optional[int]
    degree: Optional[str]


class CourseBaseInfo(BaseModel):
    persons: Optional[list[Person]]
    institutions: Optional[list[Institution]]
    class_type: Optional[str]
    class_id: Optional[str]
    class_cycle: Optional[str]
    semester: Optional[str]
    sws: Optional[float]
    max_participants: Optional[int]
    in_person_type: Optional[str]
    language: Optional[str]
    for_exchange_students: Optional[str]
    links: Optional[str]
    sigel: Optional[str]


class Session(BaseModel):
    caption: Optional[str]
    weekday: Optional[WeekdayEnum]
    starting_time: Optional[time]
    ending_time: Optional[time]
    timing_type: Optional[CourseStartTypeEnum]
    rhythm: Optional[str]
    duration_start: Optional[Date]
    duration_end: Optional[Date]
    room: Optional[str]
    lecturer: Optional[str]
    remark: Optional[str]
    cancelled_dates: Optional[str]


class Material(BaseModel):
    valid_from: Optional[Date]
    valid_to: Optional[Date]
    file_name: Optional[str]
    description: Optional[str]


class AssociatedExam(BaseModel):
    module_name: Optional[str]
    program_name: Optional[str]
    ects: Optional[int]
    module_classification: Optional[str]
    degree: Optional[str]
    module_id: Optional[str]
    exam_id: Optional[str]
    po_version: Optional[str]


class AdditionalInformation(BaseModel):
    remark: Optional[str]
    literature: Optional[str]
    date: Optional[str]
    registration: Optional[str]
    format: Optional[str]
    content: Optional[str]
    learning_content: Optional[str]
    target_group: Optional[str]
    location: Optional[str]
    comment: Optional[str]
    assessment: Optional[str]
    time: Optional[str]
    topic: Optional[str]
    short_comment: Optional[str]
    prerequisites: Optional[str]
    number: Optional[str]
    type: Optional[str]


class ExamInformation(BaseModel):
    ects: Optional[int]
    examiner: Optional[str]
    degree_program: Optional[str]
    kzfa: Optional[str]
    registration_start: Optional[Date]
    registration_end: Optional[Date]
    exam_id: Optional[str]
    program_version: Optional[str]
    degree_awarded: Optional[str]
    date: Optional[Date]


class AssociatedClass(BaseModel):
    description: Optional[str]
    weekly_hours: Optional[float]
    number: Optional[str] = Field(None)


class AssociatedTutorial(BaseModel):
    description: Optional[str]
    weekly_hours: Optional[float] = Field(None)
    number: Optional[str] = Field(None)


class EnrollmentDeadline(BaseModel):
    program_associated_deadline: Optional[str] = Field(None)
    other_deadlines: Optional[str] = Field(None)


class CourseDetails(BaseModel):
    sessions: Optional[list[Session]]
    persons: Optional[list[Person]]
    additional_information: Optional[str]
    last_updated: Optional[datetime]


class CourseBasic(BaseModel):
    """Model for a course, used to flatten the response from Directus."""

    publish_id: int
    title: str = Field(alias="name")
    sws: Optional[float]
    type: Optional[str]
    language: Optional[str]
    degree: Optional[str]


class CoursesBasic(RootModel):
    """Model for a list of courses, used to flatten the response from Directus."""

    root: List[CourseBasic] = []
