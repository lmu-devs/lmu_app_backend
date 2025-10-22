from typing import List, Optional, Dict
from pydantic import BaseModel


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


class PersonSummary(BaseModel):
    """Summary person model for list responses"""
    id: Optional[str] = None    
    name: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    academic_degree: Optional[str] = None


class Person(BaseModel):
    """Complete person model with all related data"""
    # Basic info (from people table)
    id: Optional[str] = None
    person_id: str
    name: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    academic_degree: Optional[str] = None
    
    # Related data (from other tables)
    details: Optional[PersonDetails] = None
    roles: List[PersonRole] = []