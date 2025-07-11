from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from shared.src.enums import FacultyEnum
from shared.src.models.people_model import PersonBasic, PersonSummary, PeopleResponse
from ..services.people_service import PeopleService

router = APIRouter(tags=["people"])


@router.get("/", response_model=PeopleResponse)
async def get_people(
    faculty_filter: Optional[str] = Query(None, description="Filter by faculty code"),
    limit: int = Query(50, ge=1, le=500, description="Number of people to return"),
    offset: int = Query(0, ge=0, description="Number of people to skip")
):
    """
    Get list of people with basic information (refactored schema).
    """
    service = PeopleService()
    return await service.get_all_people(
        faculty_filter=faculty_filter,
        limit=limit,
        offset=offset
    )


@router.get("/{person_id}", response_model=PersonBasic)
async def get_person_by_id(
    person_id: str
):
    """
    Get basic information about a specific person (refactored schema).
    """
    service = PeopleService()
    person = await service.get_person_by_id(person_id)
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return person

