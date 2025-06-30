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
    faculty: Optional[FacultyEnum] = Query(None, description="Filter by faculty"),
    limit: int = Query(50, ge=1, le=500, description="Number of people to return"),
    offset: int = Query(0, ge=0, description="Number of people to skip"),
    db: Session = Depends(get_db)
):
    """
    Get list of people, optionally filtered by faculty
    """
    service = PeopleService(db)
    return await service.get_people(
        faculty_filter=faculty,
        limit=limit,
        offset=offset
    )


@router.get("/by-faculty/{faculty}", response_model=PeopleResponse) 
async def get_people_by_faculty(
    faculty: FacultyEnum,
    limit: int = Query(50, ge=1, le=500, description="Number of people to return"),
    offset: int = Query(0, ge=0, description="Number of people to skip"),
    db: Session = Depends(get_db)
):
    """
    Get people from a specific faculty
    """
    service = PeopleService(db)
    return await service.get_people(
        faculty_filter=faculty,
        limit=limit,
        offset=offset
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