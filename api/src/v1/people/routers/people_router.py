from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Path
from shared.src.enums import FacultyEnum
from shared.src.models.people_model import PersonBasic, PersonSummary, PeopleResponse
from shared.src.services.directus_service import DirectusService
from pathlib import Path as FilePath

router = APIRouter(tags=["people"])

# Initialize Directus service
directus = DirectusService()

# GraphQL queries file path
graphql_path = FilePath(__file__).parent.parent / "graphql" / "new_people_queries.graphql"


@router.get("/faculty/{faculty_id}")
async def get_people_by_faculty(
    faculty_id: int = Path(..., description="Faculty ID to filter by"),
    offset: int = Query(0, ge=0, description="Number of people to skip")
) -> Dict[str, Any]:
    """
    Get people from a specific faculty using GraphQL query.
    """
    try:
        variables = {
            "faculty_enum": faculty_id,
            "offset": offset
        }
        
        response = directus.execute_query_file(
            query_file_path=graphql_path,
            variables=variables,
            operation_name="GetPeopleByFaculty"
        )
        
        people_data = response.get("data", {}).get("people", [])
        
        return {
            "faculty_id": faculty_id,
            "people": people_data,
            "total_count": len(people_data),
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
        variables = {"id": person_id}
        
        response = directus.execute_query_file(
            query_file_path=graphql_path,
            variables=variables,
            operation_name="GetPersonWithDetails"
        )
        
        person_data = response.get("data", {}).get("people_by_id")
        
        if not person_data:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return {
            "person": person_data
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
    from shared.src.services.people_service import PeopleService
    service = PeopleService()
    return await service.get_all_people(
        faculty_filter=faculty_filter,
        offset=offset
    )

