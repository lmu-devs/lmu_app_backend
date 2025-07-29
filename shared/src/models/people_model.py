from typing import List, Optional, Dict
from pydantic import BaseModel
from shared.src.enums import FacultyEnum


class PersonDetails(BaseModel):
    """Additional details for a person (stored in person_details table)"""
    id: Optional[str] = None
    person_id: str
    profile_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    office_hours: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None
    gender: Optional[str] = None
    employment_status: Optional[str] = None
    courses: List[str] = []  # Course numbers stored as JSON array


class PersonRole(BaseModel):
    """Role information for a person (stored in person_roles table)"""
    id: Optional[str] = None
    person_id: str
    role_name: Optional[str] = None
    lsf_role_enum: Optional[str] = None
    institution_name: Optional[str] = None
    institution_url: Optional[str] = None
    institutions: Optional[List[Dict]] = []


class PersonBasic(BaseModel):
    """Basic person information (stored in people table)"""
    id: Optional[str] = None
    person_id: str
    name: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    academic_degree: Optional[str] = None
    faculty_enum: Optional[FacultyEnum] = None
    primary_role: Optional[str] = None


class PersonSummary(BaseModel):
    """Summary person model for list responses"""
    id: Optional[str] = None    
    name: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    academic_degree: Optional[str] = None
    faculty_enum: Optional[FacultyEnum] = None
    primary_role: Optional[str] = None


class PersonComplete(BaseModel):
    """Complete person model with all related data"""
    # Basic info (from people table)
    id: Optional[str] = None
    person_id: str
    name: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    academic_degree: Optional[str] = None
    faculty_enum: Optional[FacultyEnum] = None
    primary_role: Optional[str] = None
    profile_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    academic_title_enum: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None
    office_hours: Optional[str] = None
    
    # Related data (from other tables)
    details: Optional[PersonDetails] = None
    roles: List[PersonRole] = []
    
    @property
    def courses(self) -> List[str]:
        """Get courses from person details"""
        return self.details.courses if self.details else []
    
    @courses.setter
    def courses(self, value: List[str]):
        """Set courses in person details"""
        if not self.details:
            self.details = PersonDetails(person_id=self.person_id)
        self.details.courses = value


class PeopleResponse(BaseModel):
    """Response model for people list endpoints"""
    people: List[PersonSummary]
    total_count: int
    faculty_filter: Optional[FacultyEnum] = None


class Person(PersonComplete):
    """Legacy Person model - maps to PersonComplete for backward compatibility"""
    
    person_id: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    academic_degree: Optional[str] = None
    
    @property
    def basic_info(self) -> Optional[PersonDetails]:
        """Legacy property that maps to details"""
        return self.details
    
    @basic_info.setter
    def basic_info(self, value: Optional[PersonDetails]):
        """Legacy setter that maps to details"""
        self.details = value

