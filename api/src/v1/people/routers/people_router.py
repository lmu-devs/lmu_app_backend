from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Path
from shared.src.enums import FacultyEnum
from shared.src.models.people_model import PersonBasic, PersonSummary, PeopleResponse
from ..services.people_service import PeopleService

router = APIRouter(tags=["people"])

# Initialize People service
people_service = PeopleService()


@router.get("/faculty/{faculty_id}")
async def get_people_by_faculty(
    faculty_id: int = Path(..., description="Faculty ID to filter by"),
    offset: int = Query(0, ge=0, description="Number of people to skip")
) -> Dict[str, Any]:
    """
    Get people from a specific faculty.
    """
    try:
        # Convert faculty_id to string for filtering (assuming faculty codes are strings)
        faculty_code = str(faculty_id) if faculty_id else None
        
        response = await people_service.get_all_people(
            faculty_filter=faculty_code,
            offset=offset
        )
        
        return {
            "faculty_id": faculty_id,
            "people": [person.dict() for person in response.people],
            "total_count": response.total_count,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch people by faculty: {str(e)}")


@router.get("/person/{person_id}")
async def get_person_with_details(
    person_id: str = Path(..., description="Person ID to retrieve")
) -> Dict[str, Any]:
    """
    Get detailed information about a specific person including roles and details.
    """
    try:
        person = await people_service.get_person_by_id(person_id)
        
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return {
            "person": person.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch person details: {str(e)}")


# Legacy endpoints (keeping for backward compatibility)
@router.get("/", response_model=PeopleResponse)
async def get_people(
    faculty_filter: Optional[str] = Query(None, description="Filter by faculty code"),
    offset: int = Query(0, ge=0, description="Number of people to skip")
):
    """
    Get list of people with basic information (refactored schema).
    """
    return await people_service.get_all_people(
        faculty_filter=faculty_filter,
        offset=offset
    )

