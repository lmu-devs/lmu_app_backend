from typing import List, Optional
from pydantic import BaseModel
from shared.src.enums import AcademicTitleEnum, LSFRoleEnum, FacultyEnum


class Institution(BaseModel):
    """Institution information for a role"""
    name: Optional[str] = None
    url: Optional[str] = None
    id: Optional[str] = None
    data: Optional[str] = None


class PersonRole(BaseModel):
    """Role information for a person"""
    lsf_role_enum: Optional[LSFRoleEnum] = None
    institutions: Optional[List[Institution]] = None

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
    # If you want, you can add status, note, office_hours here

class Person(BaseModel):
    """Complete person model with all crawled data"""
    id: str
    profile_url: Optional[str] = None
    
    # Names
    name: str  # Full name from crawler
    basic_info: Optional[PersonBasicInfo] = None
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    # Faculty information
    faculty_enum: Optional[FacultyEnum] = None
    
    # Academic information
    academic_title_enum: Optional[AcademicTitleEnum] = None
    
    # Status information
    status: Optional[str] = None
    note: Optional[str] = None
    office_hours: Optional[str] = None
    
    # Related data
    roles: List[PersonRole] = []
    courses: List[PersonCourse] = []


class PersonSummary(BaseModel):
    """Summary person model for list responses"""
    id: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    primary_role: Optional[str] = None
    faculty_enum: Optional[FacultyEnum] = None
    academic_title: Optional[str] = None


class PeopleResponse(BaseModel):
    """Response model for people list endpoints"""
    people: List[PersonSummary]
    total_count: int
    faculty_filter: Optional[FacultyEnum] = None

