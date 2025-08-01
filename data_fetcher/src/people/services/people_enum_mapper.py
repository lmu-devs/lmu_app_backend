"""
Enum Mapper Service for People Pipeline
Maps string values to appropriate enum objects
"""
from typing import Dict, List, Optional
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.enums.people_enums import (
    map_faculty_name_to_enum,
    map_academic_title_to_enum,
    map_gender_to_enum,
    map_employment_status_to_enum,
    map_lsf_role_to_enum
)

logger = get_main_fetcher_logger(__name__)


class PeopleEnumMapper:
    """Maps string values to enum objects for people data"""

    def __init__(self):
        self.logger = logger

    def map_person_enums(self, normalized_person: Dict) -> Dict:
        """
        Map all enum fields for a single person
        
        Args:
            normalized_person: Normalized person data
            
        Returns:
            Person data with enums mapped
        """
        try:
            mapped_person = normalized_person.copy()
            
            # Log courses before enum mapping
            courses_before = normalized_person.get("courses", [])
            person_name = normalized_person.get("name", "Unknown")
            self.logger.debug(f"🎓 [ENUM_MAPPER] {person_name}: Input courses count: {len(courses_before)}")
            
            # Map faculty enum
            mapped_person["faculty_enum"] = self._map_faculty_enum(
                normalized_person.get("faculty")
            )
            
            # Map academic title enum
            mapped_person["academic_title_enum"] = self._map_academic_title_enum(
                normalized_person.get("academic_title")
            )
            
            # Map basic info enums
            mapped_person["basic_info"] = self._map_basic_info_enums(
                normalized_person.get("basic_info", {})
            )
            
            # Map roles enums
            mapped_person["roles"] = self._map_roles_enums(
                normalized_person.get("roles", [])
            )
            
            # Set primary_role based on first role or employment status
            mapped_person["primary_role"] = self._determine_primary_role(
                mapped_person.get("roles", []),
                normalized_person.get("basic_info", {}).get("employment_status")
            )
            
            # Map phone enum
            mapped_person["phone_enum"] = self._map_phone_enum(
                normalized_person.get("phone")
            )
            
            # Propagate person_id if present
            if 'person_id' in normalized_person:
                mapped_person['person_id'] = normalized_person['person_id']
            
            # Log courses after enum mapping (should be same since courses are copied)
            courses_after = mapped_person.get("courses", [])
            self.logger.debug(f"🎓 [ENUM_MAPPER] {person_name}: Output courses count: {len(courses_after)}")
            
            return mapped_person
            
        except Exception as e:
            self.logger.error(f"Failed to map enums for person: {e}")
            self.logger.debug(f"Person data: {normalized_person}")
            raise

    def map_batch_enums(self, normalized_people: List[Dict]) -> List[Dict]:
        """
        Map enums for a batch of people
        
        Args:
            normalized_people: List of normalized person data
            
        Returns:
            List of person data with enums mapped
        """
        mapped_people = []
        failed_count = 0
        
        for i, person in enumerate(normalized_people):
            try:
                mapped_person = self.map_person_enums(person)
                mapped_people.append(mapped_person)
                
                if (i + 1) % 50 == 0:
                    self.logger.debug(f"Mapped enums for {i + 1}/{len(normalized_people)} people")
                    
            except Exception as e:
                failed_count += 1
                self.logger.warning(f"Failed to map enums for person {person.get('name', 'Unknown')}: {e}")
                continue
        
        self.logger.info(f"Mapped enums for {len(mapped_people)}/{len(normalized_people)} people successfully (failed: {failed_count})")
        return mapped_people

    def _map_faculty_enum(self, faculty_text: Optional[str]):
        """Map faculty text to FacultyEnum"""
        if not faculty_text:
            return None
            
        try:
            return map_faculty_name_to_enum(faculty_text)
        except Exception as e:
            self.logger.warning(f"Failed to map faculty '{faculty_text}': {e}")
            return None

    def _map_academic_title_enum(self, academic_title_text: Optional[str]):
        """Map academic title text to AcademicTitleEnum"""
        if not academic_title_text:
            return None
            
        try:
            return map_academic_title_to_enum(academic_title_text)
        except Exception as e:
            self.logger.warning(f"Failed to map academic title '{academic_title_text}': {e}")
            return None

    def _map_phone_enum(self, phone_text: Optional[str]):
        """Map phone text to phone enum (currently no phone enum exists)"""
        # No phone enum is defined in the system, so return None
        # Phone numbers are stored as plain strings
        return None

    def _map_basic_info_enums(self, basic_info: Dict) -> Dict:
        """Map enum fields in basic_info"""
        mapped_basic_info = basic_info.copy()
        
        # Map gender enum
        gender_text = basic_info.get("gender")
        if gender_text:
            try:
                mapped_basic_info["gender_enum"] = map_gender_to_enum(gender_text)
            except Exception as e:
                self.logger.warning(f"Failed to map gender '{gender_text}': {e}")
                mapped_basic_info["gender_enum"] = None
        else:
            mapped_basic_info["gender_enum"] = None
        
        # Map employment status enum
        employment_status_text = basic_info.get("employment_status")
        if employment_status_text:
            try:
                mapped_basic_info["employment_status_enum"] = map_employment_status_to_enum(employment_status_text)
            except Exception as e:
                self.logger.warning(f"Failed to map employment status '{employment_status_text}': {e}")
                mapped_basic_info["employment_status_enum"] = None
        else:
            mapped_basic_info["employment_status_enum"] = None
            
        return mapped_basic_info

    def _map_roles_enums(self, roles: List[Dict]) -> List[Dict]:
        """Map enum fields in roles"""
        mapped_roles = []
        
        for role in roles:
            mapped_role = role.copy()
            
            # Map LSF role enum
            lsf_role_text = role.get("lsf_role_enum")
            if lsf_role_text:
                try:
                    mapped_role["lsf_role_enum_obj"] = map_lsf_role_to_enum(lsf_role_text)
                except Exception as e:
                    self.logger.warning(f"Failed to map LSF role '{lsf_role_text}': {e}")
                    mapped_role["lsf_role_enum_obj"] = None
            else:
                mapped_role["lsf_role_enum_obj"] = None
                
            mapped_roles.append(mapped_role)
            
        return mapped_roles

    def _determine_primary_role(self, roles: List[Dict], employment_status: Optional[str]) -> Optional[str]:
        """Determine primary role from roles list or employment status"""
        # First try to get from roles
        if roles and len(roles) > 0:
            first_role = roles[0]
            # Check for role_name first (set by normalizer)
            if first_role.get("role_name"):
                return first_role.get("role_name")
            # Fallback to lsf_role_enum (raw value)
            elif first_role.get("lsf_role_enum"):
                return first_role.get("lsf_role_enum")
        
        # Fallback to employment status
        if employment_status:
            return employment_status
        
        return None

    def get_enum_statistics(self, mapped_people: List[Dict]) -> Dict:
        """Get statistics about enum mapping success rates"""
        stats = {
            "total_people": len(mapped_people),
            "faculty_mapped": 0,
            "academic_title_mapped": 0,
            "gender_mapped": 0,
            "employment_status_mapped": 0,
            "roles_mapped": 0,
            "faculty_values": {},
            "academic_title_values": {},
            "gender_values": {},
            "employment_status_values": {},
            "role_values": {}
        }
        
        for person in mapped_people:
            # Count successful mappings
            if person.get("faculty_enum"):
                stats["faculty_mapped"] += 1
                faculty_code = getattr(person["faculty_enum"], 'code', str(person["faculty_enum"]))
                stats["faculty_values"][faculty_code] = stats["faculty_values"].get(faculty_code, 0) + 1
                
            if person.get("academic_title_enum"):
                stats["academic_title_mapped"] += 1
                title_value = getattr(person["academic_title_enum"], 'value', str(person["academic_title_enum"]))
                stats["academic_title_values"][title_value] = stats["academic_title_values"].get(title_value, 0) + 1
            
            basic_info = person.get("basic_info", {})
            if basic_info.get("gender_enum"):
                stats["gender_mapped"] += 1
                gender_value = getattr(basic_info["gender_enum"], 'value', str(basic_info["gender_enum"]))
                stats["gender_values"][gender_value] = stats["gender_values"].get(gender_value, 0) + 1
                
            if basic_info.get("employment_status_enum"):
                stats["employment_status_mapped"] += 1
                status_value = getattr(basic_info["employment_status_enum"], 'value', str(basic_info["employment_status_enum"]))
                stats["employment_status_values"][status_value] = stats["employment_status_values"].get(status_value, 0) + 1
            
            roles = person.get("roles", [])
            for role in roles:
                if role.get("lsf_role_enum_obj"):
                    stats["roles_mapped"] += 1
                    role_value = getattr(role["lsf_role_enum_obj"], 'value', str(role["lsf_role_enum_obj"]))
                    stats["role_values"][role_value] = stats["role_values"].get(role_value, 0) + 1
        
        # Calculate percentages
        if stats["total_people"] > 0:
            stats["faculty_mapped_percent"] = (stats["faculty_mapped"] / stats["total_people"]) * 100
            stats["academic_title_mapped_percent"] = (stats["academic_title_mapped"] / stats["total_people"]) * 100
            stats["gender_mapped_percent"] = (stats["gender_mapped"] / stats["total_people"]) * 100
            stats["employment_status_mapped_percent"] = (stats["employment_status_mapped"] / stats["total_people"]) * 100
        
        return stats 