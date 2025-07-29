"""
Model Mapper Service for People Pipeline
Maps normalized data to Pydantic models with validation
"""
from typing import Dict, List, Optional
from pydantic import ValidationError
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.models.people_model import (
    Person, PersonDetails, PersonRole
)

logger = get_main_fetcher_logger(__name__)


class PeopleModelMapper:
    """Maps normalized data to Pydantic models with validation"""

    def __init__(self):
        self.logger = logger

    def map_to_person_model(self, mapped_person: Dict) -> Person:
        """
        Map a single person's data to Person model
        
        Args:
            mapped_person: Person data with enums mapped
            
        Returns:
            Validated Person model instance
        """
        try:
            # Map basic info
            basic_info_data = mapped_person.get("basic_info", {})
            
            # Convert enum objects to string values for PersonDetails model validation
            gender_enum = basic_info_data.get("gender_enum")
            gender_value = gender_enum.value if gender_enum else None
            
            employment_status_enum = basic_info_data.get("employment_status_enum")
            employment_status_value = employment_status_enum.value if employment_status_enum else None
            
            basic_info = PersonDetails(
                person_id=mapped_person["person_id"],
                first_name=basic_info_data.get("first_name"),
                last_name=basic_info_data.get("last_name"),
                gender=gender_value,
                title=basic_info_data.get("title"),
                academic_degree=basic_info_data.get("academic_degree"),
                employment_status=employment_status_value,
                name_suffix=basic_info_data.get("name_suffix")
            )
            
            # Map roles
            roles = []
            for role_data in mapped_person.get("roles", []):
                # Flatten institutions if present (use first institution for legacy fields)
                institution = None
                institution_url = None
                if role_data.get("institutions"):
                    first_inst = role_data["institutions"][0]
                    institution = first_inst.get("name")
                    institution_url = first_inst.get("url")
                
                # Convert enum object to string for PersonRole model
                lsf_role_enum = role_data.get("lsf_role_enum_obj")
                lsf_role_enum_str = lsf_role_enum.value if lsf_role_enum else None
                
                role = PersonRole(
                    person_id=mapped_person["person_id"],
                    role_name=role_data.get("role_name"),
                    lsf_role_enum=lsf_role_enum_str,
                    institution=institution,
                    institution_url=institution_url
                )
                roles.append(role)
            
            # Map courses to simple list of course numbers
            courses = []
            for course_data in mapped_person.get("courses", []):
                course_number = course_data.get("number")
                if course_number:
                    courses.append(course_number)
            
            # Create Person model
            person = Person(
                id=None,
                person_id=mapped_person["person_id"],
                profile_url=mapped_person.get("profile_url"),
                name=mapped_person["name"],
                first_name=basic_info_data.get("first_name"),
                surname=basic_info_data.get("last_name"),
                title=basic_info_data.get("title"),
                academic_degree=basic_info_data.get("academic_degree"),
                basic_info=basic_info,
                email=mapped_person.get("email"),
                phone=mapped_person.get("phone"),
                address=mapped_person.get("address"),
                faculty_enum=mapped_person.get("faculty_enum"),
                academic_title_enum=mapped_person.get("academic_title_enum"),
                status=basic_info_data.get("status"),
                note=basic_info_data.get("note"),
                office_hours=basic_info_data.get("office_hours"),
                roles=roles,
                courses=courses
            )
            
            return person
            
        except ValidationError as e:
            self.logger.error(f"Validation error for person {mapped_person.get('name', 'Unknown')}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to map person to model: {e}")
            self.logger.debug(f"Person data: {mapped_person}")
            raise

    def map_batch_to_models(self, mapped_people: List[Dict]) -> List[Person]:
        """
        Map a batch of people data to Person models
        
        Args:
            mapped_people: List of person data with enums mapped
            
        Returns:
            List of validated Person model instances
        """
        person_models = []
        failed_count = 0
        validation_errors = []
        
        for i, person_data in enumerate(mapped_people):
            try:
                person_model = self.map_to_person_model(person_data)
                person_models.append(person_model)
                
                if (i + 1) % 50 == 0:
                    self.logger.debug(f"Mapped {i + 1}/{len(mapped_people)} people to models")
                    
            except ValidationError as e:
                failed_count += 1
                error_info = {
                    "person_name": person_data.get("name", "Unknown"),
                    "person_id": person_data.get("person_id", "Unknown"),
                    "errors": str(e)
                }
                validation_errors.append(error_info)
                self.logger.warning(f"Validation failed for person {error_info['person_name']}: {e}")
                continue
            except Exception as e:
                failed_count += 1
                self.logger.warning(f"Failed to map person {person_data.get('name', 'Unknown')} to model: {e}")
                continue
        
        self.logger.info(f"Mapped {len(person_models)}/{len(mapped_people)} people to models successfully (failed: {failed_count})")
        
        if validation_errors:
            self.logger.warning(f"Found {len(validation_errors)} validation errors")
            for error in validation_errors[:5]:
                self.logger.debug(f"Validation error sample: {error}")
        
        return person_models

    def get_model_statistics(self, person_models: List[Person]) -> Dict:
        """Get statistics about the mapped models"""
        stats = {
            "total_models": len(person_models),
            "models_with_email": 0,
            "models_with_phone": 0,
            "models_with_address": 0,
            "models_with_faculty": 0,
            "models_with_academic_title": 0,
            "models_with_roles": 0,
            "models_with_courses": 0,
            "total_roles": 0,
            "total_courses": 0,
            "average_roles_per_person": 0,
            "average_courses_per_person": 0
        }
        
        total_roles = 0
        total_courses = 0
        
        for person in person_models:
            if person.email:
                stats["models_with_email"] += 1
            if person.phone:
                stats["models_with_phone"] += 1
            if person.address:
                stats["models_with_address"] += 1
            if person.faculty_enum:
                stats["models_with_faculty"] += 1
            if person.academic_title_enum:
                stats["models_with_academic_title"] += 1
            if person.roles:
                stats["models_with_roles"] += 1
                total_roles += len(person.roles)
            if person.courses:
                stats["models_with_courses"] += 1
                total_courses += len(person.courses)
        
        stats["total_roles"] = total_roles
        stats["total_courses"] = total_courses
        
        if stats["total_models"] > 0:
            stats["average_roles_per_person"] = total_roles / stats["total_models"]
            stats["average_courses_per_person"] = total_courses / stats["total_models"]
            
            # Calculate percentages
            stats["email_coverage_percent"] = (stats["models_with_email"] / stats["total_models"]) * 100
            stats["phone_coverage_percent"] = (stats["models_with_phone"] / stats["total_models"]) * 100
            stats["address_coverage_percent"] = (stats["models_with_address"] / stats["total_models"]) * 100
            stats["faculty_coverage_percent"] = (stats["models_with_faculty"] / stats["total_models"]) * 100
            stats["academic_title_coverage_percent"] = (stats["models_with_academic_title"] / stats["total_models"]) * 100
            stats["roles_coverage_percent"] = (stats["models_with_roles"] / stats["total_models"]) * 100
            stats["courses_coverage_percent"] = (stats["models_with_courses"] / stats["total_models"]) * 100
        
        return stats

    def validate_models_integrity(self, person_models: List[Person]) -> Dict:
        """Validate the integrity of the mapped models"""
        integrity_report = {
            "total_models": len(person_models),
            "valid_models": 0,
            "issues": {
                "missing_required_fields": [],
                "invalid_emails": [],
                "invalid_phones": [],
                "empty_names": [],
                "invalid_urls": []
            }
        }
        
        for person in person_models:
            is_valid = True
            
            # Check required fields
            if not person.person_id or not person.name:
                integrity_report["issues"]["missing_required_fields"].append({
                    "person_id": person.person_id,
                    "name": person.name
                })
                is_valid = False
            
            # Check email format (basic)
            if person.email and '@' not in person.email:
                integrity_report["issues"]["invalid_emails"].append({
                    "person_id": person.person_id,
                    "email": person.email
                })
                is_valid = False
                
            # Check phone format (basic)
            if person.phone and not person.phone.isdigit():
                integrity_report["issues"]["invalid_phones"].append({
                    "person_id": person.person_id,
                    "phone": person.phone
                })
                is_valid = False
            
            # Check for empty names
            if not person.name or person.name.strip() == "":
                integrity_report["issues"]["empty_names"].append({
                    "person_id": person.person_id,
                    "name": person.name
                })
                is_valid = False
            
            # Check URL format (basic)
            if person.profile_url and not person.profile_url.startswith(('http://', 'https://')):
                integrity_report["issues"]["invalid_urls"].append({
                    "person_id": person.person_id,
                    "url": person.profile_url
                })
                is_valid = False
            
            if is_valid:
                integrity_report["valid_models"] += 1
        
        # Calculate validity percentage
        if integrity_report["total_models"] > 0:
            integrity_report["validity_percent"] = (integrity_report["valid_models"] / integrity_report["total_models"]) * 100
        
        return integrity_report 