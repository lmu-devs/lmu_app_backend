from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from shared.src.core.database import get_db
from shared.src.enums import FacultyEnum
from ..models.people_model import Person, PersonSummary, PeopleResponse
from ..services.people_service import PeopleService

router = APIRouter(tags=["people"])


@router.get("/", response_model=PeopleResponse)
async def get_people(
    faculty_id: Optional[int] = Query(None, description="Filter by faculty ID"),
    limit: int = Query(50, ge=1, le=500, description="Number of people to return (only when no filters applied)"),
    offset: int = Query(0, ge=0, description="Number of people to skip (only when no filters applied)"),
    db: Session = Depends(get_db)
):
    """
    Get list of people, optionally filtered by faculty ID.
    Pagination is only applied when no faculty filter is provided.
    """
    service = PeopleService(db)
    
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
        return await service.get_people(
            faculty_id_filter=faculty_id,
            apply_pagination=False
        )


@router.get("/by-faculty-enum/{faculty}", response_model=PeopleResponse) 
async def get_people_by_faculty_enum(
    faculty: FacultyEnum,
    db: Session = Depends(get_db)
):
    """
    Get all people from a specific faculty by faculty enum (no pagination)
    """
    service = PeopleService(db)
    return await service.get_people(
        faculty_filter=faculty,
        apply_pagination=False
    )



@router.get("/{person_id}", response_model=Person)
async def get_person_by_id(
    person_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific person
    """
    service = PeopleService(db)
    person = await service.get_person_by_id(person_id)
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return person


@router.get("/faculties/", response_model=dict)
async def get_available_faculties(db: Session = Depends(get_db)):
    """
    Get list of faculties that have people data
    """
    service = PeopleService(db)
    return await service.get_available_faculties()