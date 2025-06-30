from typing import List, Optional
from pydantic import BaseModel, RootModel
from shared.src.enums import AcademicTitle, LSFRole, FacultyEnum


class PersonRole(BaseModel):
    """Role information for a person"""
    institution: Optional[str] = None
    role: Optional[str] = None
    institution_url: Optional[str] = None
    lsf_role_id: Optional[int] = None
    lsf_role_name: Optional[str] = None
    lsf_role_enum: Optional[LSFRole] = None


class PersonCourse(BaseModel):
    """Course information for a person"""
    course_number: Optional[str] = None
    course_name: Optional[str] = None
    semester: Optional[str] = None
    course_url: Optional[str] = None


class PersonBasicInfo(BaseModel):
    """Basic personal information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    title: Optional[str] = None
    academic_degree: Optional[str] = None
    employment_status: Optional[str] = None
    name_suffix: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None
    office_hours: Optional[str] = None


class Person(BaseModel):
    """Complete person model with all crawled data"""
    id: str
    profile_url: Optional[str] = None
    
    # Names
    name: str  # Full name from crawler
    basic_info: PersonBasicInfo
    
    # Contact information
    email: Optional[str] = None
    address: Optional[str] = None
    
    # Faculty information
    faculty: Optional[str] = None
    faculty_id: Optional[str] = None
    faculty_enum: Optional[FacultyEnum] = None
    
    # Academic information
    academic_title_enum: Optional[AcademicTitle] = None
    
    # Related data
    roles: List[PersonRole] = []
    courses: List[PersonCourse] = []


class PersonSummary(BaseModel):
    """Simplified person model for list views"""
    id: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    primary_role: Optional[str] = None
    email: Optional[str] = None
    faculty: Optional[str] = None
    faculty_id: Optional[str] = None
    faculty_enum: Optional[FacultyEnum] = None
    academic_title: Optional[str] = None


class PeopleResponse(BaseModel):
    """Response model for people lists"""
    people: List[PersonSummary]
    total_count: int
    faculty_filter: Optional[FacultyEnum] = None


class People(RootModel):
    """Root model for backward compatibility"""
    root: List[Person] | list = []