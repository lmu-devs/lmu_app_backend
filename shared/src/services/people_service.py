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
from shared.src.models.people_model import (
    Person, PersonSummary, PeopleResponse, PersonRole, PersonCourse, PersonDetails, PersonBasic
)
from shared.src.enums import FacultyEnum
from shared.src.enums.people_enums import LSFRoleEnum

logger = get_main_fetcher_logger(__name__)


class PeopleService:
    """Comprehensive service for people data operations (read/write)"""
    
    def __init__(self, test_mode: bool = False):
        self.directus = DirectusService()
        self.logger = logger
        self.test_mode = test_mode
        
        # Use the same pattern as university_service.py
        base_path = Path(__file__).parent.parent.parent.parent
        self.graphql_path = base_path / "api" / "src" / "v1" / "people" / "graphql"
        
        # Constants
        self.QUERIES_FILE = "new_people_queries.graphql"
        self.MUTATIONS_FILE = "mutations.graphql"

    # ==================== READ OPERATIONS ====================

    async def get_all_people(
        self, 
        faculty_filter: Optional[str] = None,
        limit: Optional[int] = 50, 
        offset: int = 0
    ) -> PeopleResponse:
        """Get all people from CMS with optional faculty filtering"""
        
        query_path = self.graphql_path / self.QUERIES_FILE
        
        # Build variables for the query
        variables = {
            "limit": limit,
            "offset": offset
        }
        
        # Note: Faculty filtering is not implemented yet due to CMS schema issues
        if faculty_filter:
            self.logger.warning(f"Faculty filtering not implemented yet: {faculty_filter}")
        
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=variables,
            operation_name="GetAllPeople"
        )
        
        people_raw: List[dict[str, Any]] = response["data"]["people"]
        
        # Convert to PersonSummary objects
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
                first_name=person_data.get("first_name"),
                surname=person_data.get("surname"),
                title=person_data.get("title"),
                academic_degree=person_data.get("academic_degree"),
                faculty_enum=faculty_enum,
                primary_role=person_data.get("primary_role")
            )
            people_summaries.append(person_summary)
        
        return PeopleResponse(
            people=people_summaries,
            total_count=len(people_summaries),
            faculty_filter=faculty_filter
        )

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Get detailed information about a specific person from CMS"""
        
        query_path = self.graphql_path / self.QUERIES_FILE
        variables = {"id": person_id}
        
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=variables,
            operation_name="GetPersonById"
        )
        
        person_data = response["data"]["people_by_id"]
        if not person_data:
            return None
        
        # Get roles and courses
        roles_data = await self.get_people_roles(person_id)
        courses_data = await self.get_people_courses(person_id)
        
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
                institution=role_data.get("institution"),
                institution_url=role_data.get("institution_url"),
                institutions=role_data.get("institutions", [])
            )
            roles.append(role)
        
        # Convert courses
        courses = []
        for course_data in courses_data:
            course = PersonCourse(
                person_id=person_id,
                course_number=course_data.get("course_number"),
                course_name=course_data.get("course_name"),
                semester=course_data.get("semester"),
                course_url=course_data.get("course_url")
            )
            courses.append(course)
        
        # Get person details
        details_data = await self.get_person_details(person_id)
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
        
        # Map faculty enum
        faculty_enum = None
        if person_data.get("faculty_enum"):
            try:
                faculty_enum = next(f for f in FacultyEnum if f.id == person_data["faculty_enum"])
            except StopIteration:
                pass
        
        return Person(
            id=person_data["id"],
            profile_url=person_data.get("profile_url"),
            name=person_data["name"],
            first_name=person_data.get("first_name"),
            surname=person_data.get("surname"),
            title=person_data.get("title"),
            academic_degree=person_data.get("academic_degree"),
            faculty_enum=faculty_enum,
            primary_role=person_data.get("primary_role"),
            email=details_data.get("email") if details_data else None,
            phone=details_data.get("phone") if details_data else None,
            address=details_data.get("address") if details_data else None,
            academic_title_enum=person_data.get("academic_title_enum"),
            status=details_data.get("status") if details_data else None,
            note=details_data.get("note") if details_data else None,
            office_hours=details_data.get("office_hours") if details_data else None,
            details=details,
            roles=roles,
            courses=courses
        )

    async def get_people_roles(self, person_id: str) -> List[Dict]:
        """Get roles for a specific person from CMS"""
        try:
            query_path = self.graphql_path / self.QUERIES_FILE
            result = self.directus.execute_query_file(query_path, {"person_id": person_id}, operation_name="GetPersonRoles")
            return result.get("data", {}).get("person_roles", [])
        except Exception:
            return []

    async def get_people_courses(self, person_id: str) -> List[Dict]:
        """Get courses for a specific person from CMS"""
        try:
            query_path = self.graphql_path / self.QUERIES_FILE
            result = self.directus.execute_query_file(query_path, {"person_id": person_id}, operation_name="GetPersonCourses")
            return result.get("data", {}).get("person_courses", [])
        except Exception:
            return []

    async def get_person_details(self, person_id: str) -> Optional[Dict]:
        """Get details for a specific person from CMS"""
        try:
            query_path = self.graphql_path / self.QUERIES_FILE
            result = self.directus.execute_query_file(query_path, {"person_id": person_id}, operation_name="GetPersonDetails")
            details = result.get("data", {}).get("person_details", [])
            return details[0] if details else None
        except Exception:
            return None

    async def get_available_faculties(self) -> Dict[str, any]:
        """Get list of faculties that have people data from CMS"""
        
        # Get all people to extract faculty information
        all_people = await self.get_all_people(limit=10000)  # Get all people
        
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

    # ==================== WRITE OPERATIONS ====================

    def collect_and_store_people(self, people_data: List[Dict]):
        """
        Collect and store people data in Directus CMS
        
        Args:
            people_data: List of people data dictionaries
        """
        self.logger.info("⬆️  Collecting and storing people data in Directus CMS...")
        self.logger.info(f"TEST MODE: {self.test_mode}")
        self.logger.info(f"📋 Found {len(people_data)} people to process")
        
        stored_count = 0
        skipped_count = 0
        
        for person_data in people_data:
            try:
                person_id = person_data.get("person_id")
                if not person_id:
                    self.logger.warning(f"❌ Person data missing person_id: {person_data.get('name', 'UNKNOWN')}")
                    continue
                
                # Check if person already exists
                existing_person = self._check_person_exists(person_id)
                if existing_person:
                    self.logger.debug(f"⏭️  Person {person_data.get('name', 'UNKNOWN')} already exists, skipping")
                    skipped_count += 1
                    continue
                
                # Create new person
                self._create_new_person(person_id, person_data)
                
                # Add roles if present
                if person_data.get("roles"):
                    self._upsert_person_roles(person_id, person_data)
                
                # Add courses if present
                if person_data.get("courses"):
                    self._upsert_person_courses(person_id, person_data)
                
                stored_count += 1
                self.logger.debug(f"✅ Successfully processed person: {person_data.get('name', 'UNKNOWN')}")
                
            except Exception as e:
                self.logger.error(f"   ❌ Failed to process person {person_data.get('name', 'UNKNOWN')}: {e}")
                continue
        
        self.logger.info(f"📊 Processing complete: {stored_count} stored, {skipped_count} skipped, {len(people_data) - stored_count - skipped_count} failed")

    def _check_person_exists(self, person_id: str) -> bool:
        """Check if a person already exists in the CMS"""
        try:
            query_path = self.graphql_path / self.QUERIES_FILE
            variables = {"person_id": person_id}
            
            response = self.directus.execute_query_file(
                query_path,
                variables,
                operation_name="GetPersonByPersonId"
            )
            people = response.get("data", {}).get("people", [])
            return len(people) > 0
            
        except Exception as e:
            self.logger.debug(f"Error checking if person {person_id} exists: {e}")
            return False

    def _create_new_person(self, person_id: str, person_data: dict):
        """Create a new person record in CMS using GraphQL mutation"""
        basic_info = person_data.get("basic_info", {})
        
        # Helper functions for enum handling
        def get_enum_value(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            return str(enum_obj) if enum_obj else None
        
        def get_enum_id(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'id'):
                return enum_obj.id
            if hasattr(enum_obj, 'code'):
                return enum_obj.code
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            return str(enum_obj) if enum_obj else None

        # Debug logging for enum values
        self.logger.debug(f"🔍 DEBUG ENUMS for {person_data.get('name', 'UNKNOWN')}:" )
        self.logger.debug(f"   faculty_enum: {person_data.get('faculty_enum')} (type: {type(person_data.get('faculty_enum'))})")
        self.logger.debug(f"   academic_title_enum: {person_data.get('academic_title_enum')} (type: {type(person_data.get('academic_title_enum'))})")
        self.logger.debug(f"   gender_enum: {basic_info.get('gender_enum')} (type: {type(basic_info.get('gender_enum'))})")
        self.logger.debug(f"   employment_status_enum: {basic_info.get('employment_status_enum')} (type: {type(basic_info.get('employment_status_enum'))})")
        self.logger.debug(f"   RAW faculty: {person_data.get('faculty_enum')} (type: {type(person_data.get('faculty_enum'))})")
        self.logger.debug(f"   RAW academic_title: {person_data.get('academic_title_enum')} (type: {type(person_data.get('academic_title_enum'))})")

        # 1. Create main person record
        person_data_clean = {
            "person_id": person_id,
            "name": person_data.get("name", "")
        }
        
        # Only add fields with actual values
        if basic_info.get("first_name"):
            person_data_clean["first_name"] = basic_info.get("first_name")
        if basic_info.get("last_name"):
            person_data_clean["surname"] = basic_info.get("last_name")
        if basic_info.get("title"):
            person_data_clean["title"] = basic_info.get("title")
        if basic_info.get("academic_degree"):
            person_data_clean["academic_degree"] = basic_info.get("academic_degree")
        
        # Handle faculty_enum properly - convert to integer ID
        faculty_enum = person_data.get("faculty_enum")
        if faculty_enum:
            faculty_id = get_enum_id(faculty_enum)
            if faculty_id is not None:
                person_data_clean["faculty_enum"] = faculty_id
                self.logger.debug(f"Set faculty_enum to {faculty_id} for {person_data.get('name', 'UNKNOWN')}")
            else:
                self.logger.warning(f"Could not get faculty ID for {faculty_enum} for {person_data.get('name', 'UNKNOWN')}")
        else:
            self.logger.debug(f"No faculty_enum provided for {person_data.get('name', 'UNKNOWN')}")
        
        person_variables = {"data": person_data_clean}
        
        if self.test_mode:
            self.logger.info(f"🆕 CREATE PERSON: {person_variables}")
        else:
            try:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                response = self.directus.execute_query_file(
                    query_path,
                    person_variables,
                    operation_name="CreatePerson"
                )
                self.logger.info(f"CMS response: {response}")
            except Exception as e:
                self.logger.error(f"CMS CreatePerson error: {e}")
                self.logger.error(f"Failed data: {person_variables}")
                # Log the exact error details if available
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    self.logger.error(f"Response text: {e.response.text}")
                if hasattr(e, 'response') and hasattr(e.response, 'json'):
                    try:
                        error_json = e.response.json()
                        self.logger.error(f"Response JSON: {error_json}")
                    except:
                        pass
                raise

        # 2. Create person details record
        details_data_clean = {
            "person_id": person_id  # This should be the UUID from the created person, not the string person_id
        }
        
        # Only add fields with actual values
        if person_data.get("profile_url"):
            details_data_clean["profile_url"] = person_data.get("profile_url")
        if person_data.get("email"):
            details_data_clean["email"] = person_data.get("email")
        if person_data.get("phone"):
            details_data_clean["phone"] = person_data.get("phone")
        if person_data.get("address"):
            details_data_clean["address"] = person_data.get("address")
        if basic_info.get("office_hours"):
            details_data_clean["office_hours"] = basic_info.get("office_hours")
        if basic_info.get("status"):
            details_data_clean["status"] = basic_info.get("status")
        if basic_info.get("note"):
            details_data_clean["note"] = basic_info.get("note")
        
        # Handle enum values properly
        gender_enum = basic_info.get("gender_enum")
        if gender_enum:
            gender_value = get_enum_value(gender_enum)
            if gender_value is not None:
                details_data_clean["gender"] = gender_value
        
        employment_status_enum = basic_info.get("employment_status_enum")
        if employment_status_enum:
            employment_value = get_enum_value(employment_status_enum)
            if employment_value is not None:
                details_data_clean["employment_status"] = employment_value
            
        details_variables = {"data": details_data_clean}
        
        if self.test_mode:
            self.logger.info(f"🆕 CREATE PERSON DETAILS: {details_variables}")
        else:
            try:
                # First, get the person's UUID by person_id
                person_uuid = self._get_person_uuid_by_person_id(person_id)
                if person_uuid:
                    # Update the details_data_clean to use the UUID reference object
                    details_data_clean["person_id"] = {"id": person_uuid}  # Pass as reference object
                    details_variables = {"data": details_data_clean}
                    
                    query_path = self.graphql_path / self.MUTATIONS_FILE
                    response = self.directus.execute_query_file(
                        query_path,
                        details_variables,
                        operation_name="CreatePersonDetails"
                    )
                    self.logger.info(f"CMS details response: {response}")
                else:
                    self.logger.warning(f"Could not find person UUID for person_id: {person_id}")
            except Exception as e:
                self.logger.error(f"CMS CreatePersonDetails error: {e}")
                self.logger.error(f"Failed details data: {details_variables}")
                # Don't raise here, as the main person was created successfully

    def _update_existing_person(self, person_id: str, person_data: dict):
        """Update existing person with new data using GraphQL mutation"""
        basic_info = person_data.get("basic_info", {})
        
        # Helper functions for enum handling
        def get_enum_value(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            return str(enum_obj) if enum_obj else None
        
        def get_enum_id(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'id'):
                return enum_obj.id
            if hasattr(enum_obj, 'code'):
                return enum_obj.code
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            return str(enum_obj) if enum_obj else None

        # 1. Update main person record
        person_updates = {}
        if person_data.get("name"):
            person_updates["name"] = person_data.get("name")
        if basic_info.get("first_name"):
            person_updates["first_name"] = basic_info.get("first_name")
        if basic_info.get("last_name"):
            person_updates["surname"] = basic_info.get("last_name")
        if basic_info.get("title"):
            person_updates["title"] = basic_info.get("title")
        if basic_info.get("academic_degree"):
            person_updates["academic_degree"] = basic_info.get("academic_degree")
        if get_enum_id(person_data.get("faculty_enum")):
            person_updates["faculty_enum"] = get_enum_id(person_data.get("faculty_enum"))
        if person_data.get("primary_role"):
            person_updates["primary_role"] = person_data.get("primary_role")
            
        if person_updates:
            person_variables = {
                "id": person_id,
                "data": person_updates
            }
            if self.test_mode:
                self.logger.info(f"🔄 UPDATE PERSON: {person_variables}")
            else:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                self.directus.execute_query_file(
                    query_path, 
                    person_variables,
                    operation_name="UpdatePerson"
                )

        # 2. Update person details record
        details_updates = {}
        if person_data.get("profile_url"):
            details_updates["profile_url"] = person_data.get("profile_url")
        if person_data.get("email"):
            details_updates["email"] = person_data.get("email")
        if person_data.get("phone"):
            details_updates["phone"] = person_data.get("phone")
        if person_data.get("address"):
            details_updates["address"] = person_data.get("address")
        if basic_info.get("office_hours"):
            details_updates["office_hours"] = basic_info.get("office_hours")
        if basic_info.get("status"):
            details_updates["status"] = basic_info.get("status")
        if basic_info.get("note"):
            details_updates["note"] = basic_info.get("note")
        if get_enum_value(basic_info.get("gender_enum")):
            details_updates["gender"] = get_enum_value(basic_info.get("gender_enum"))
        if get_enum_value(basic_info.get("employment_status_enum")):
            details_updates["employment_status"] = get_enum_value(basic_info.get("employment_status_enum"))
            
        if details_updates:
            details_variables = {
                "person_id": person_id,
                "data": details_updates
            }
            if self.test_mode:
                self.logger.info(f"🔄 UPDATE PERSON DETAILS: {details_variables}")
            else:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                self.directus.execute_query_file(
                    query_path, 
                    details_variables,
                    operation_name="UpdatePersonDetails"
                )

    def _upsert_person_roles(self, person_id: str, person_data: dict):
        """Add roles for this person using GraphQL mutation"""
        roles = person_data.get("roles", [])
        self.logger.info(f"Upserting roles for {person_id}: {roles}")
        
        def get_enum_value(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            return str(enum_obj) if enum_obj else None
        
        # Get the person's UUID
        person_uuid = self._get_person_uuid_by_person_id(person_id)
        if not person_uuid:
            self.logger.warning(f"Could not find person UUID for person_id: {person_id}, skipping roles")
            return
        
        for role in roles:
            lsf_role_enum = role.get("lsf_role_enum_obj")
            
            # Get institution info (use first institution if multiple)
            institutions = role.get("institutions", [])
            institution_name = institutions[0].get("name", "") if institutions else ""
            institution_url = institutions[0].get("url", "") if institutions else ""
            
            variables = {
                "data": {
                    "person_id": {"id": person_uuid},  # Pass as reference object
                    "role_name": role.get("role_name", ""),
                    "lsf_role_enum": get_enum_value(lsf_role_enum),
                    "institution": institution_name,
                    "institution_url": institution_url
                }
            }
            if self.test_mode:
                self.logger.info(f"🏢 CREATE ROLE: {variables}")
            else:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                self.directus.execute_query_file(
                    query_path, 
                    variables,
                    operation_name="CreatePersonRole"
                )

    def _upsert_person_courses(self, person_id: str, person_data: dict):
        """Add courses for this person using GraphQL mutation"""
        courses = person_data.get("courses", [])
        self.logger.info(f"Upserting courses for {person_id}: {courses}")
        
        # Get the person's UUID
        person_uuid = self._get_person_uuid_by_person_id(person_id)
        if not person_uuid:
            self.logger.warning(f"Could not find person UUID for person_id: {person_id}, skipping courses")
            return
        
        for course in courses:
            variables = {
                "data": {
                    "person_id": {"id": person_uuid},  # Pass as reference object
                    "course_number": course.get("number", ""),
                    "course_name": course.get("name", ""),
                    "semester": course.get("semester", ""),
                    "course_url": course.get("url", "")
                }
            }
            if self.test_mode:
                self.logger.info(f"📚 CREATE COURSE: {variables}")
            else:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                self.directus.execute_query_file(
                    query_path, 
                    variables,
                    operation_name="CreatePersonCourse"
                )

    def _generate_person_id(self, person_data: dict) -> str:
        """Generate a unique ID for the person"""
        name = person_data.get("name", "")
        profile_url = person_data.get("profile_url", "")
        
        if profile_url:
            # Extract ID from URL if possible
            match = re.search(r'personal\.pid=(\d+)', profile_url)
            if match:
                return f"lmu_person_{match.group(1)}"
        
        # Fallback: generate hash-based ID
        content = f"{name}_{profile_url}"
        return f"lmu_person_{hashlib.md5(content.encode()).hexdigest()[:8]}"

    def test_cms_connection(self) -> Dict:
        """Test CMS connection and validate schema"""
        try:
            # Test basic query - use the same pattern as university service
            query_path = self.graphql_path / self.QUERIES_FILE
            variables = {"limit": 1, "offset": 0}
            
            response = self.directus.execute_query_file(
                query_path,
                variables
            )
            
            return {
                "success": True,
                "message": "CMS connection successful",
                "response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"CMS connection failed: {e}",
                "error": str(e)
            }

    def validate_person_schema(self, person_data: Dict) -> Dict:
        """Validate person data against expected schema"""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ["id", "name"]
        for field in required_fields:
            if not person_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Check faculty_enum
        faculty_enum = person_data.get("faculty_enum")
        if faculty_enum:
            if hasattr(faculty_enum, 'id'):
                warnings.append(f"faculty_enum should be integer ID, got: {faculty_enum.id} (type: {type(faculty_enum.id)})")
            else:
                warnings.append(f"faculty_enum should be integer ID, got: {faculty_enum} (type: {type(faculty_enum)})")
        
        # Check basic_info structure
        basic_info = person_data.get("basic_info", {})
        if basic_info:
            # Check enum fields in basic_info
            for enum_field in ["gender_enum", "employment_status_enum"]:
                enum_value = basic_info.get(enum_field)
                if enum_value and hasattr(enum_value, 'value'):
                    warnings.append(f"{enum_field} should be string value, got: {enum_value.value} (type: {type(enum_value.value)})") 

    def _get_person_uuid_by_person_id(self, person_id: str) -> Optional[str]:
        """Get person's UUID by their person_id string"""
        try:
            query_path = self.graphql_path / self.QUERIES_FILE
            variables = {"person_id": person_id}
            
            response = self.directus.execute_query_file(
                query_path,
                variables,
                operation_name="GetPersonByPersonId"
            )
            people = response.get("data", {}).get("people", [])
            if people:
                return people[0].get("id")  # Return the UUID
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting person UUID for person_id {person_id}: {e}")
            return None 