"""
People Service - API Layer
Simple wrapper around the consolidated PeopleService
"""
from typing import Optional
from shared.src.enums import FacultyEnum
from shared.src.models.people_model import Person, PeopleResponse
from shared.src.services.people_service import PeopleService

# Create a single instance of the consolidated service
_people_service = PeopleService()


async def get_all_people(
    faculty_filter: Optional[FacultyEnum] = None,
    faculty_code_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    apply_pagination: bool = True
) -> PeopleResponse:
    """Get list of people with optional faculty filter and conditional pagination"""
    
    # Determine faculty code to filter by
    faculty_code = None
    if faculty_filter:
        faculty_code = faculty_filter.code
    elif faculty_code_filter:
        faculty_code = faculty_code_filter
    
    return await _people_service.get_all_people(
        faculty_filter=faculty_code,
        offset=offset if apply_pagination else 0
    )


async def get_person_by_id(person_id: str) -> Optional[Person]:
    """Get detailed information about a specific person"""
    return await _people_service.get_person_by_id(person_id)


async def get_available_faculties() -> dict:
    """Get list of faculties that have people data"""
    return await _people_service.get_available_faculties() 