from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from shared.src.enums import FacultyEnum
from shared.src.models.people_model import Person, PersonSummary, PeopleResponse
from ..services.people_directus_service import PeopleAPIService

router = APIRouter(tags=["people"])


@router.get("/", response_model=PeopleResponse)
async def get_people(
    faculty_id: Optional[int] = Query(None, description="Filter by faculty ID"),
    limit: int = Query(50, ge=1, le=500, description="Number of people to return (only when no filters applied)"),
    offset: int = Query(0, ge=0, description="Number of people to skip (only when no filters applied)")
):
    """
    Get list of people, optionally filtered by faculty ID.
    Pagination is only applied when no faculty filter is provided.
    """
    service = PeopleAPIService()
    
    # Only apply pagination when no faculty filter is provided
    if faculty_id is None:
        # No filter - use pagination
        return await service.get_people(
            limit=limit,
            offset=offset,
            apply_pagination=True
        )
    else:
        # Faculty filter provided - no pagination
        try:
            faculty_enum = next(f for f in FacultyEnum if f.id == faculty_id)
        except StopIteration:
            raise HTTPException(status_code=400, detail="Invalid faculty ID")
        
        return await service.get_people(
            faculty_filter=faculty_enum,
            apply_pagination=False
        )


@router.get("/faculty_code/{faculty_code}", response_model=PeopleResponse)
async def get_people_by_faculty_code(
    faculty_code: str
):
    """
    Get all people from a specific faculty by faculty code (no pagination)
    """
    service = PeopleAPIService()
    return await service.get_people(
        faculty_code_filter=faculty_code,
        apply_pagination=False
    )
    
@router.get("/faculty_id/{faculty_id}", response_model=PeopleResponse)
async def get_people_by_faculty_id(
    faculty_id: int
):
    """
    Get all people from a specific faculty by faculty ID (no pagination)
    """
    service = PeopleAPIService()
    try:
        faculty_enum = next(f for f in FacultyEnum if f.id == faculty_id)
    except StopIteration:
        raise HTTPException(status_code=400, detail="Invalid faculty ID")
    
    return await service.get_people(
        faculty_filter=faculty_enum,
        apply_pagination=False
    )


@router.get("/{person_id}", response_model=Person)
async def get_person_by_id(
    person_id: str
):
    """
    Get detailed information about a specific person
    """
    service = PeopleAPIService()
    person = await service.get_person_by_id(person_id)
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return person


@router.get("/faculties/available")
async def get_available_faculties():
    """
    Get list of faculties that have people data
    """
    service = PeopleAPIService()
    return await service.get_available_faculties()

