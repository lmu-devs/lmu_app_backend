"""
Comprehensive People Service
Consolidates all people-related operations (read/write) from CMS
"""
import hashlib
import re
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

from shared.src.core.logging import get_main_fetcher_logger
from shared.src.services.directus_service import DirectusService
from ..models.people_model import (
    Person, PersonSummary, PeopleResponse, PersonRole, PersonDetails, PersonBasic
)
from shared.src.enums import FacultyEnum
from shared.src.enums.people_enums import LSFRoleEnum

logger = get_main_fetcher_logger(__name__)


class PeopleService:
    """Comprehensive service for people data operations (read/write)"""
    
    def __init__(self):
        self.directus = DirectusService()
        self.logger = logger
        
        # GraphQL queries path for API layer
        base_path = Path(__file__).parent.parent
        self.graphql_path = base_path / "graphql"
        
        # GraphQL query files
        self.GET_ALL_PEOPLE_FILE = "get_all_people.graphql"
        self.GET_PERSON_BY_ID_FILE = "get_person_by_id.graphql"
        self.GET_PERSON_ROLES_FILE = "get_person_roles.graphql"
        self.GET_PERSON_DETAILS_FILE = "get_person_details.graphql"
        self.MUTATIONS_FILE = "mutations.graphql"

    # ==================== READ OPERATIONS ====================

    async def get_all_people(
        self, 
        faculty_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None
    ) -> PeopleResponse:
        """Get all people from CMS with optional faculty filtering"""
        
        query_path = self.graphql_path / self.GET_ALL_PEOPLE_FILE
        
        # Build variables for the query
        variables = {}
        if offset is not None:
            variables["offset"] = offset
        if limit is not None:
            variables["limit"] = limit
        else:
            # Set a high limit to get all people (Directus default is 100)
            variables["limit"] = 10000
        
        # Use faculty filtering if provided
        if faculty_id:
            query_path = self.graphql_path / "people_queries.graphql"
            variables["faculty_id"] = faculty_id
            # Use the GetPeopleByFaculty query instead
            response = self.directus.query(
                """
                query GetPeopleByFaculty($faculty_id: String!, $offset: Int, $limit: Int) {
                    people(filter: { faculty: { id: { _eq: $faculty_id } } }, offset: $offset, limit: $limit) {
                        id
                        name
                        first_name
                        surname
                        academic_degree
                        faculty {
                            id
                        }
                    }
                }
                """,
                variables
            )
        else:
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables=variables
            )
        
        # Check if response has expected structure
        if "data" not in response:
            self.logger.error(f"Unexpected response structure: {response}")
            raise ValueError(f"Invalid response structure: missing 'data' key")
        
        if "people" not in response["data"]:
            self.logger.error(f"Unexpected data structure: {response['data']}")
            raise ValueError(f"Invalid data structure: missing 'people' key")
        
        people_raw: List[dict[str, Any]] = response["data"]["people"]
        
        # Convert to PersonSummary objects
        people_summaries = []
        for person_data in people_raw:
            # Map faculty relation if present
            faculty_enum = None
            if person_data.get("faculty"):
                faculty_data = person_data["faculty"]
                try:
                    # Look up faculty enum by the relation's id (convert string to int)
                    faculty_id_int = int(faculty_data["id"])
                    faculty_enum = next(f for f in FacultyEnum if f.id == faculty_id_int)
                except (StopIteration, ValueError):
                    pass
            
            person_summary = PersonSummary(
                id=person_data["id"],
                name=person_data["name"],
                first_name=person_data.get("first_name"),
                surname=person_data.get("surname"),
                academic_degree=person_data.get("academic_degree")
            )
            people_summaries.append(person_summary)
        
        # Convert faculty_id to enum for response
        faculty_enum_filter = None
        if faculty_id:
            try:
                faculty_id_int = int(faculty_id)
                faculty_enum_filter = next(f for f in FacultyEnum if f.id == faculty_id_int)
            except (StopIteration, ValueError):
                self.logger.warning(f"Invalid faculty id: {faculty_id}")
        
        return PeopleResponse(
            people=people_summaries,
            total_count=len(people_summaries),
            faculty_filter=faculty_enum_filter
        )

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Get detailed information about a specific person from CMS"""
        
        query_path = self.graphql_path / self.GET_PERSON_BY_ID_FILE
        variables = {"id": person_id}
        
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=variables
        )
        
        # Check if response has expected structure
        if "data" not in response:
            self.logger.error(f"Unexpected response structure: {response}")
            raise ValueError(f"Invalid response structure: missing 'data' key")
        
        if "people_by_id" not in response["data"]:
            self.logger.error(f"Unexpected data structure: {response['data']}")
            raise ValueError(f"Invalid data structure: missing 'people_by_id' key")
        
        person_data = response["data"]["people_by_id"]
        if not person_data:
            return None
        
        # Get roles and courses
        roles_data = await self._get_people_roles(person_id)
        courses_data = await self._get_people_courses(person_id)
        
        # Convert roles
        roles = []
        for role_data in roles_data:
            lsf_role_enum = None
            if role_data.get("lsf_role_enum"):
                try:
                    lsf_role_enum = LSFRoleEnum(role_data["lsf_role_enum"])
                except ValueError:
                    self.logger.warning(f"Invalid LSFRole enum value: {role_data['lsf_role_enum']}")
            
            role = PersonRole(
                person_id=person_id,
                role_name=role_data.get("role_name"),
                lsf_role_enum=lsf_role_enum,
                institution_name=role_data.get("institution_name"),
                institution_url=role_data.get("institution_url"),
                institutions=role_data.get("institutions", [])
            )
            roles.append(role)
        
        # Convert courses (simplified - just use the course list)
        courses = courses_data
        
        # Get person details
        details_data = await self._get_person_details(person_id)
        details = None
        if details_data:
            details = PersonDetails(
                person_id=person_id,
                profile_url=details_data.get("profile_url"),
                email=details_data.get("email"),
                phone=details_data.get("phone"),
                address=details_data.get("address"),
                office_hours=details_data.get("office_hours"),
                status=details_data.get("status"),
                note=details_data.get("note"),
                gender=details_data.get("gender"),
                employment_status=details_data.get("employment_status")
            )
        
        # Map faculty relation
        faculty_enum = None
        if person_data.get("faculty"):
            faculty_data = person_data["faculty"]
            try:
                # Look up faculty enum by the relation's id (convert string to int)
                faculty_id_int = int(faculty_data["id"])
                faculty_enum = next(f for f in FacultyEnum if f.id == faculty_id_int)
            except (StopIteration, ValueError):
                pass
        
        return Person(
            id=person_data["id"],
            person_id=person_data.get("person_id", person_id),  # Use provided person_id or fallback to parameter
            name=person_data["name"],
            first_name=person_data.get("first_name"),
            surname=person_data.get("surname"),
            academic_degree=person_data.get("academic_degree"),
            academic_title_enum=person_data.get("academic_title_enum"),
            details=details,
            roles=roles,
            courses=courses
        )

    async def _get_people_roles(self, person_id: str) -> List[Dict]:
        """Get roles for a specific person from CMS"""
        try:
            query_path = self.graphql_path / self.GET_PERSON_ROLES_FILE
            result = self.directus.execute_query_file(query_path, {"person_id": person_id})
            return result.get("data", {}).get("person_roles", [])
        except Exception:
            return []

    async def _get_people_courses(self, person_id: str) -> List[str]:
        """Get courses for a specific person from CMS (from person_details.courses)"""
        try:
            # Get person details which includes courses as a JSON array
            person_details = await self._get_person_details(person_id)
            if person_details and person_details.get("courses"):
                return person_details["courses"]
            return []
        except Exception:
            return []

    async def _get_person_details(self, person_id: str) -> Optional[Dict]:
        """Get details for a specific person from CMS"""
        try:
            query_path = self.graphql_path / self.GET_PERSON_DETAILS_FILE
            result = self.directus.execute_query_file(query_path, {"person_id": person_id})
            details = result.get("data", {}).get("person_details", [])
            return details[0] if details else None
        except Exception:
            return None

    async def get_available_faculties(self) -> Dict[str, any]:
        """Get list of faculties that have people data from CMS"""
        
        # Get all people to extract faculty information
        all_people = await self.get_all_people()  # Get all people
        
        faculty_counts = {}
        faculty_names = {}
        
        for person in all_people.people:
            faculty_enum = person.faculty_enum
            
            if faculty_enum:
                faculty_code = faculty_enum.code
                if faculty_code not in faculty_counts:
                    faculty_counts[faculty_code] = 0
                    faculty_names[faculty_code] = faculty_enum.name
                faculty_counts[faculty_code] += 1
        
        faculties = []
        for faculty_code, count in faculty_counts.items():
            faculty_info = {
                "id": faculty_code,
                "name": faculty_names.get(faculty_code, faculty_code),
                "enum": faculty_code,
                "people_count": count
            }
            faculties.append(faculty_info)
        
        # Sort by name
        faculties.sort(key=lambda x: x["name"])
        
        return {
            "faculties": faculties,
            "total_faculties": len(faculties)
        }
