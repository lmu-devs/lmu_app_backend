import hashlib
import re
from typing import List, Dict, Optional, Union
from pathlib import Path
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.services.directus_service import DirectusService


class PeopleCMSService:
    def __init__(self, test_mode: bool = True):
        self.directus = DirectusService()
        self.logger = get_main_fetcher_logger(__name__)
        self.graphql_path = Path(__file__).parent.parent / "graphql" / "people"
        self.test_mode = test_mode
        print("DEBUG: logger name in PeopleCMSService:", self.logger.name, flush=True)

    def collect_and_store_people(self, people_data: List[Dict]):
        """Collect people data and store in Directus CMS"""
        print("DEBUG: collect_and_store_people called", flush=True)
        self.logger.info("⬆️  Collecting and storing people data in Directus CMS...")
        
        self.logger.info(f"TEST MODE: {self.test_mode}")
        
        total_people_processed = 0
        successful_people = 0
        failed_people = 0
        
        self.logger.info(f"📋 Found {len(people_data)} people to process")
        
        for i, person_data in enumerate(people_data, 1):
            try:
                # Process and store person in CMS
                person_id = self._generate_person_id(person_data)
                
                # Always try to create first, then update if it exists
                try:
                    self._create_new_person(person_id, person_data)
                    self.logger.debug(f"   🆕 Created new person: {person_data.get('name', 'Unknown')}")
                except Exception as create_error:
                    # If creation fails due to duplicate, try updating
                    if "RECORD_NOT_UNIQUE" in str(create_error) or "unique" in str(create_error).lower():
                        try:
                            self.logger.debug(f"   🔄 Person {person_id} exists, updating instead")
                            self._update_existing_person(person_id, person_data)
                            self.logger.debug(f"   ✅ Updated existing person: {person_data.get('name', 'Unknown')}")
                        except Exception as update_error:
                            self.logger.warning(f"   ⚠️  Failed to update existing person {person_data.get('name', 'Unknown')}: {update_error}")
                            # Continue processing this person's roles and courses even if main record failed
                    else:
                        # Re-raise if it's a different error
                        self.logger.error(f"   ❌ Unexpected error creating person {person_data.get('name', 'Unknown')}: {create_error}")
                        raise create_error
                
                # Process roles and courses regardless of create/update outcome
                self._upsert_person_roles(person_id, person_data)
                self._upsert_person_courses(person_id, person_data)
                
                successful_people += 1
                total_people_processed += 1
                
            except Exception as e:
                failed_people += 1
                self.logger.error(f"   ❌ Failed to process person {person_data.get('name', 'Unknown')}: {str(e)}")
                continue
        
       

    def _create_new_person(self, person_id: str, person_data: dict):
        """Create a new person record in Directus using GraphQL mutation"""
        print("DEBUG: _create_new_person called", flush=True)
        basic_info = person_data.get("basic_info", {})
        
        # Use the enum objects that were already mapped by the enum mapper
        faculty_enum = person_data.get("faculty_enum")
        academic_title_enum = person_data.get("academic_title_enum")
        gender_enum = basic_info.get("gender_enum")
        employment_status_enum = basic_info.get("employment_status_enum")
        
        # Debug logging to see what enum values we have
        self.logger.debug(f"🔍 DEBUG ENUMS for {person_data.get('name', 'Unknown')}:")
        self.logger.debug(f"   faculty_enum: {faculty_enum} (type: {type(faculty_enum)})")
        self.logger.debug(f"   academic_title_enum: {academic_title_enum} (type: {type(academic_title_enum)})")
        self.logger.debug(f"   gender_enum: {gender_enum} (type: {type(gender_enum)})")
        self.logger.debug(f"   employment_status_enum: {employment_status_enum} (type: {type(employment_status_enum)})")
        
        # Debug raw data to understand why faculty is None
        raw_faculty = person_data.get('faculty')
        raw_academic_title = person_data.get('academic_title')
        self.logger.debug(f"   RAW faculty: '{raw_faculty}' (type: {type(raw_faculty)})")
        self.logger.debug(f"   RAW academic_title: '{raw_academic_title}' (type: {type(raw_academic_title)})")
        
        # Helper function to safely get enum value
        def get_enum_value(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            # If it's a string, return it directly
            return str(enum_obj) if enum_obj else None
        
        # Helper function to safely get enum id/code
        def get_enum_id(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'id'):
                return enum_obj.id
            if hasattr(enum_obj, 'code'):
                return enum_obj.code
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            # If it's a string, return it directly
            return str(enum_obj) if enum_obj else None

        variables = {
            "data": {
                "id": person_id,
                "profile_url": person_data.get("profile_url"),
                "name": person_data.get("name", ""),
                "basic_info": {
                    "first_name": basic_info.get("first_name", ""),
                    "last_name": basic_info.get("last_name", ""),
                    "gender": get_enum_value(gender_enum),
                    "title": basic_info.get("title", ""),
                    "academic_degree": basic_info.get("academic_degree", ""),
                    "employment_status": get_enum_value(employment_status_enum),
                    "name_suffix": basic_info.get("name_suffix", ""),
                },
                "status": basic_info.get("status", ""),
                "note": basic_info.get("note", ""),
                "office_hours": basic_info.get("office_hours", ""),
                "email": person_data.get("email", ""),
                "phone": person_data.get("phone", ""),
                "adress": person_data.get("address", ""),
                "faculty_enum": get_enum_id(faculty_enum),
                "academic_title_enum": get_enum_value(academic_title_enum),
            }
        }
        
        if self.test_mode:
            self.logger.info(f"🆕 CREATE PERSON: {variables}")
        else:
            self.logger.info(f"🆕 CREATE PERSON: {variables}")
            response = self.directus.execute_query_file(
                self.graphql_path / "mutations.graphql",
                variables,
                operation_name="CreatePerson"
            )
            self.logger.info(f"CMS response: {response}")

    def _update_existing_person(self, person_id: str, person_data: dict):
        """Update existing person with new data using GraphQL mutation"""
        basic_info = person_data.get("basic_info", {})
        
        # Use the enum objects that were already mapped by the enum mapper
        faculty_enum = person_data.get("faculty_enum")
        academic_title_enum = person_data.get("academic_title_enum")
        gender_enum = basic_info.get("gender_enum")
        employment_status_enum = basic_info.get("employment_status_enum")
        
        # Helper function to safely get enum value
        def get_enum_value(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            # If it's a string, return it directly
            return str(enum_obj) if enum_obj else None
        
        # Helper function to safely get enum id/code
        def get_enum_id(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'id'):
                return enum_obj.id
            if hasattr(enum_obj, 'code'):
                return enum_obj.code
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            # If it's a string, return it directly
            return str(enum_obj) if enum_obj else None
        
        updates = {
            "profile_url": person_data.get("profile_url"),
            "name": person_data.get("name", ""),
            "basic_info": {
                "first_name": basic_info.get("first_name", ""),
                "last_name": basic_info.get("last_name", ""),
                "gender": get_enum_value(gender_enum),
                "title": basic_info.get("title", ""),
                "academic_degree": basic_info.get("academic_degree", ""),
                "employment_status": get_enum_value(employment_status_enum),
                "name_suffix": basic_info.get("name_suffix", ""),
            },
            "status": basic_info.get("status", ""),
            "note": basic_info.get("note", ""),
            "office_hours": basic_info.get("office_hours", ""),
            "email": person_data.get("email", ""),
            "phone": person_data.get("phone", ""),
            "adress": person_data.get("address", ""),
            "faculty_enum": get_enum_id(faculty_enum),
            "academic_title_enum": get_enum_value(academic_title_enum),
        }
        
        # Only include fields that have values
        filtered_updates = {k: v for k, v in updates.items() if v and v.strip()}
        
        if filtered_updates:
            variables = {
                "id": person_id,
                "data": filtered_updates
            }
            if self.test_mode:
                self.logger.info(f"🔄 UPDATE PERSON: {variables}")
            else:
                self.directus.execute_query_file(self.graphql_path / "mutations.graphql", variables)

    def _upsert_person_roles(self, person_id: str, person_data: dict):
        """Add roles for this person using GraphQL mutation"""
        roles = person_data.get("roles", [])
        self.logger.info(f"Upserting roles for {person_id}: {roles}")
        
        # Helper function to safely get enum value
        def get_enum_value(enum_obj):
            if enum_obj is None:
                return None
            if hasattr(enum_obj, 'value'):
                return enum_obj.value
            # If it's a string, return it directly
            return str(enum_obj) if enum_obj else None
        
        for role in roles:
            # Use the enum object that was already mapped by the enum mapper
            lsf_role_enum = role.get("lsf_role_enum_obj")
            
            variables = {
                "data": {
                    "people": person_id,
                    "lsf_role_enum": get_enum_value(lsf_role_enum),
                    "institutions": role.get("institutions", [])
                }
            }
            if self.test_mode:
                self.logger.info(f"🏢 CREATE ROLE: {variables}")
            else:
                self.directus.execute_query_file(self.graphql_path / "mutations.graphql", variables)

    def _upsert_person_courses(self, person_id: str, person_data: dict):
        """Add courses for this person using GraphQL mutation"""
        courses = person_data.get("courses", [])
        self.logger.info(f"Upserting courses for {person_id}: {courses}")
        for course in courses:
            variables = {
                "data": {
                    "people": person_id,
                    "course_number": course.get("number", ""),
                    "course_name": course.get("name", ""),
                    "semester": course.get("semester", ""),
                    "course_url": course.get("url", "")
                }
            }
            if self.test_mode:
                self.logger.info(f"📚 CREATE COURSE: {variables}")
            else:
                self.directus.execute_query_file(self.graphql_path / "mutations.graphql", variables)

    def _get_person_by_id(self, person_id: str) -> Optional[Dict]:
        """Get person by ID from Directus using GraphQL query"""
        if self.test_mode:
            self.logger.info(f"🔍 GET PERSON: {person_id}")
            return None  # In test mode, assume person doesn't exist
        try:
            result = self.directus.execute_query_file(self.graphql_path / "queries.graphql", {"id": person_id})
            return result.get("data", {}).get("people_by_pk")
        except Exception:
            return None

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

    def _generate_hash(self, person_data: dict) -> str:
        """Generate a hash of the person data for change detection"""
        # Create a string representation of the data
        data_str = str(sorted(person_data.items()))
        return hashlib.md5(data_str.encode()).hexdigest()

    def get_all_people(self, faculty_filter: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict:
        """Get all people from Directus with optional filtering using GraphQL query"""
        where_clause = {}
        if faculty_filter:
            where_clause["faculty_enum"] = {"_eq": faculty_filter}
        
        variables = {
            "where": where_clause,
            "limit": limit,
            "offset": offset
        }
        
        result = self.directus.execute_query_file(self.graphql_path / "queries.graphql", variables)
        data = result.get("data", {})
        
        return {
            "data": data.get("people", []),
            "meta": {
                "filter_count": data.get("people_aggregate", {}).get("aggregate", {}).get("count", 0)
            }
        }

    def get_person_by_id(self, person_id: str) -> Optional[Dict]:
        """Get a specific person by ID from Directus"""
        return self._get_person_by_id(person_id)

    def get_people_roles(self, person_id: str) -> List[Dict]:
        """Get roles for a specific person from Directus using GraphQL query"""
        try:
            result = self.directus.execute_query_file(self.graphql_path / "queries.graphql", {"person_id": person_id})
            return result.get("data", {}).get("people_roles", [])
        except Exception:
            return []

    def get_people_courses(self, person_id: str) -> List[Dict]:
        """Get courses for a specific person from Directus using GraphQL query"""
        try:
            result = self.directus.execute_query_file(self.graphql_path / "queries.graphql", {"person_id": person_id})
            return result.get("data", {}).get("people_courses", [])
        except Exception:
            return [] 