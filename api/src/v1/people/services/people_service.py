import logging

from typing import Any, List, Optional
from pathlib import Path

from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService
from shared.src.models.people_model import Person, PersonSummary, PeopleResponse
from shared.src.enums import FacultyEnum

# Add logger
logger = logging.getLogger(__name__)

GRAPHQL_FOLDER_NAME = "graphql"
PEOPLE_QUERY_NAME = "people_query.graphql"
PERSON_BY_ID_QUERY_NAME = "person_by_id_query.graphql"


class PeopleService:
    """Service to interact with people data from Directus using GraphQL."""

    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_all_people(
        self, 
        faculty_filter: Optional[str] = None,
        limit: Optional[int] = 50, 
        offset: int = 0
    ) -> PeopleResponse:
        """Fetches all people from Directus using GraphQL."""
        
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = PEOPLE_QUERY_NAME
        query_path = base_path / folder / query_name
        
        # Simplified variables for testing
        variables = {
            "limit": limit,
            "offset": offset
        }
        
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=variables
        )
        
        people_raw: List[dict[str, Any]] = response["data"]["people"]
        
        # Convert to PersonSummary objects - simplified for testing
        people_summaries = []
        for person_data in people_raw:
            # Map faculty enum if present
            faculty_enum = None
            if person_data.get("faculty_enum"):
                try:
                    faculty_enum = next(f for f in FacultyEnum if f.id == person_data["faculty_enum"])
                except StopIteration:
                    pass
            
            person_summary = PersonSummary(
                id=person_data["id"],
                name=person_data["name"],
                first_name=None,  # Will add later when basic_info works
                last_name=None,   # Will add later when basic_info works
                primary_role=None,
                faculty_enum=faculty_enum,
                academic_title=None  # Will add later
            )
            people_summaries.append(person_summary)
        
        return PeopleResponse(
            people=people_summaries,
            total_count=len(people_summaries),
            faculty_filter=next((f for f in FacultyEnum if f.code == faculty_filter), None) if faculty_filter else None
        )

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Fetches a specific person by ID from Directus using GraphQL."""
        
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = PERSON_BY_ID_QUERY_NAME
        query_path = base_path / folder / query_name
        
        variables = {"id": person_id}
        
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=variables
        )
        
        person_data = response["data"]["people_by_id"]
        
        if not person_data:
            return None
        
        # Map faculty enum (simplified)
        faculty_enum = None
        if person_data.get("faculty_enum"):
            try:
                faculty_enum = next(f for f in FacultyEnum if f.id == person_data["faculty_enum"])
            except StopIteration:
                pass
        
        return Person(
            id=person_data["id"],
            profile_url=None,  # Simplified for testing
            name=person_data["name"],
            basic_info=None,  # Simplified for testing
            email=person_data.get("email"),
            phone=person_data.get("phone"),
            address=None,  # Simplified for testing
            faculty_enum=faculty_enum,
            roles=[],
            courses=[]
        ) 