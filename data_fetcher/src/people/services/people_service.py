"""
People Service - Data Collection Layer
Focused on data collection and CMS write operations
"""
import hashlib
import re
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

from shared.src.core.logging import get_main_fetcher_logger
from shared.src.services.directus_service import DirectusService
from shared.src.enums import FacultyEnum

logger = get_main_fetcher_logger(__name__)


class PeopleService:
    """Service focused on people data collection and CMS write operations"""
    
    def __init__(self):
        self.directus = DirectusService()
        self.logger = logger
        
        # Point to the API GraphQL files from data_fetcher (5 levels up to project root)
        base_path = Path(__file__).parent.parent.parent.parent.parent
        self.graphql_path = base_path / "api" / "src" / "v1" / "people" / "graphql"
        
        # Constants
        self.QUERIES_FILE = "people_queries.graphql"
        self.MUTATIONS_FILE = "mutations.graphql"

    # ==================== WRITE OPERATIONS ====================

    def collect_and_store_people(self, people_data: List[dict]):
        """
        Main method to collect and store people data in Directus CMS
        Each person_data should have the structure from PeopleModelMapper
        """
        self.logger.info("⬆️  Collecting and storing people data in Directus CMS...")
        self.logger.info(f"📋 Found {len(people_data)} people to process")
        
        stored_count = 0
        failed_count = 0
        
        for person_data in people_data:
            try:
                person_id = person_data.get("person_id")
                if not person_id:
                    self.logger.error(f"Person data missing person_id: {person_data}")
                    failed_count += 1
                    continue
                
                # Check if person already exists by person_id
                existing_person = self._get_person_by_person_id(person_id)
                
                if existing_person:
                    self.logger.debug(f"Person {person_id} already exists, updating...")
                    self._update_existing_person(person_id, person_data)
                else:
                    self.logger.debug(f"Creating new person {person_id}...")
                    self._create_new_person(person_id, person_data)
                
                # Add roles if present
                if person_data.get("roles"):
                    self._upsert_person_roles(person_id, person_data)
                
                stored_count += 1
                self.logger.debug(f"✅ Successfully processed person: {person_data.get('name', 'UNKNOWN')}")
                
            except Exception as e:
                failed_count += 1
                self.logger.error(f"❌ Failed to process person {person_data.get('name', 'UNKNOWN')}: {e}")
                continue
        
        self.logger.info(f"📊 Storage summary: {stored_count}/{len(people_data)} people stored successfully (failed: {failed_count})")

    def _create_new_person(self, person_id: str, person_data: dict):
        """Create a new person record along with their details"""
        
        # 1. Create main person record
        basic_info = person_data.get("basic_info", {})
        
        person_data_clean = {
            "person_id": person_id,
            "name": person_data.get("name", ""),
            "primary_role": person_data.get("primary_role", "")
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
        
        # Handle enums properly by extracting their values
        faculty_enum = person_data.get("faculty_enum")
        if faculty_enum:
            faculty_value = self.get_enum_value(faculty_enum)
            if faculty_value is not None:
                person_data_clean["faculty_enum"] = faculty_value
                self.logger.debug(f"Using faculty_enum: {faculty_value} for {person_data.get('name', 'UNKNOWN')}")
            else:
                self.logger.debug(f"Invalid faculty_enum provided for {person_data.get('name', 'UNKNOWN')}")
        else:
            self.logger.debug(f"No faculty_enum provided for {person_data.get('name', 'UNKNOWN')}")
        
        person_variables = {"data": person_data_clean}
        
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
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                self.logger.error(f"Response text: {e.response.text}")
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_json = e.response.json()
                    self.logger.error(f"Response JSON: {error_json}")
                except:
                    pass
            raise

        # 2. Create person details record (including courses)
        details_data_clean = {
            "person_id": person_id
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
        
        # Add courses as JSON array
        courses = person_data.get("courses", [])
        if courses:
            details_data_clean["courses"] = courses
        
        # Handle enum values properly
        gender_enum = basic_info.get("gender_enum")
        if gender_enum:
            gender_value = self.get_enum_value(gender_enum)
            if gender_value is not None:
                details_data_clean["gender"] = gender_value
        
        employment_status_enum = basic_info.get("employment_status_enum")
        if employment_status_enum:
            employment_value = self.get_enum_value(employment_status_enum)
            if employment_value is not None:
                details_data_clean["employment_status"] = employment_value
            
        details_variables = {"data": details_data_clean}
        
        try:
            person_uuid = self._get_person_uuid_by_person_id(person_id)
            if person_uuid:
                details_data_clean["person_id"] = {"id": person_uuid}
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

    def _update_existing_person(self, person_id: str, person_data: dict):
        """Update an existing person record and their details"""
        
        # 1. Update main person record
        basic_info = person_data.get("basic_info", {})
        
        person_updates = {
            "name": person_data.get("name", ""),
            "primary_role": person_data.get("primary_role", "")
        }
        
        # Only update fields with actual values
        if basic_info.get("first_name"):
            person_updates["first_name"] = basic_info.get("first_name")
        if basic_info.get("last_name"):
            person_updates["surname"] = basic_info.get("last_name")
        if basic_info.get("title"):
            person_updates["title"] = basic_info.get("title")
        if basic_info.get("academic_degree"):
            person_updates["academic_degree"] = basic_info.get("academic_degree")
        
        # Handle faculty enum
        faculty_enum = person_data.get("faculty_enum")
        if faculty_enum:
            faculty_value = self.get_enum_value(faculty_enum)
            if faculty_value is not None:
                person_updates["faculty_enum"] = faculty_value
        
        # Get person's UUID for updating
        person_uuid = self._get_person_uuid_by_person_id(person_id)
        if person_uuid:
            person_variables = {
                "id": person_uuid,
                "data": person_updates
            }
            try:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                self.directus.execute_query_file(
                    query_path,
                    person_variables,
                    operation_name="UpdatePerson"
                )
            except Exception as e:
                self.logger.error(f"CMS UpdatePerson error: {e}")
                self.logger.error(f"Failed data: {person_variables}")
                raise

        # 2. Update person details record (including courses)
        details_updates = {}
        
        # Only update fields with actual values
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
        
        # Update courses as JSON array
        courses = person_data.get("courses", [])
        details_updates["courses"] = courses
        
        # Handle enum values
        gender_enum = basic_info.get("gender_enum")
        if gender_enum:
            gender_value = self.get_enum_value(gender_enum)
            if gender_value is not None:
                details_updates["gender"] = gender_value
        
        employment_status_enum = basic_info.get("employment_status_enum")
        if employment_status_enum:
            employment_value = self.get_enum_value(employment_status_enum)
            if employment_value is not None:
                details_updates["employment_status"] = employment_value
        
        # Get details UUID for updating
        details_uuid = self._get_person_details_uuid_by_person_id(person_id)
        if details_uuid and details_updates:
            details_variables = {
                "id": details_uuid,
                "data": details_updates
            }
            
            try:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                self.directus.execute_query_file(
                    query_path,
                    details_variables,
                    operation_name="UpdatePersonDetails"
                )
            except Exception as e:
                self.logger.error(f"CMS UpdatePersonDetails error: {e}")
                self.logger.error(f"Failed details data: {details_variables}")
                raise

    def _upsert_person_roles(self, person_id: str, person_data: dict):
        """Add roles for this person using GraphQL mutation"""
        roles = person_data.get("roles", [])
        self.logger.info(f"Upserting roles for {person_id}: {roles}")
        
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
                    "lsf_role_enum": self.get_enum_value(lsf_role_enum),
                    "institution_name": institution_name,
                    "institution_url": institution_url
                }
            }
            try:
                query_path = self.graphql_path / self.MUTATIONS_FILE
                self.directus.execute_query_file(
                    query_path, 
                    variables,
                    operation_name="CreatePersonRole"
                )
            except Exception as e:
                self.logger.error(f"CMS CreatePersonRole error: {e}")
                self.logger.error(f"Failed data: {variables}")
                raise

    def _get_person_by_person_id(self, person_id: str) -> Optional[Dict]:
        """Check if a person exists by person_id and return their data"""
        try:
            query_path = self.graphql_path / self.QUERIES_FILE
            variables = {"person_id": person_id}
            
            response = self.directus.execute_query_file(
                query_path,
                variables,
                operation_name="GetPersonByPersonId"
            )
            people = response.get("data", {}).get("people", [])
            return people[0] if people else None
            
        except Exception as e:
            self.logger.debug(f"Error checking if person {person_id} exists: {e}")
            return None

    def _get_person_details_uuid_by_person_id(self, person_id: str) -> Optional[str]:
        """Get the UUID of person_details record by person_id"""
        try:
            # First get the person's UUID
            person_uuid = self._get_person_uuid_by_person_id(person_id)
            if not person_uuid:
                return None
                
            query_path = self.graphql_path / self.QUERIES_FILE
            variables = {"person_id": person_uuid}
            
            response = self.directus.execute_query_file(
                query_path,
                variables,
                operation_name="GetPersonDetails"
            )
            details = response.get("data", {}).get("person_details", [])
            return details[0]["id"] if details else None
            
        except Exception as e:
            self.logger.debug(f"Error getting person details UUID for {person_id}: {e}")
            return None

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

    def get_enum_value(self, enum_obj):
        """Extract value from enum object safely"""
        if enum_obj is None:
            return None
        
        # For FacultyEnum and other enums that have an 'id' property, use that
        if hasattr(enum_obj, 'id'):
            return enum_obj.id
        
        # For simple enums that have a value property
        if hasattr(enum_obj, 'value'):
            return enum_obj.value
            
        return str(enum_obj) if enum_obj else None

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