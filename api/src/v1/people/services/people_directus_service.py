from typing import Optional, Dict
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.enums.people_enums import LSFRoleEnum
from shared.src.services.people_cms_service import PeopleCMSService
from shared.src.enums import FacultyEnum
from shared.src.models.people_model import (
    Person, PersonSummary, PeopleResponse, PersonRole, PersonCourse, PersonBasicInfo
)

logger = get_main_fetcher_logger(__name__)


class PeopleAPIService:
    def __init__(self):
        self.cms_service = PeopleCMSService()

    async def get_people(
        self,
        faculty_filter: Optional[FacultyEnum] = None,
        faculty_code_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        apply_pagination: bool = True
    ) -> PeopleResponse:
        """Get list of people from CMS with optional faculty filter and conditional pagination"""
        
        # Determine faculty code to filter by
        faculty_code = None
        if faculty_filter:
            faculty_code = faculty_filter.code
        elif faculty_code_filter:
            faculty_code = faculty_code_filter
        
        # Get people from CMS
        cms_response = self.cms_service.get_all_people(
            faculty_filter=faculty_code,
            limit=limit if apply_pagination else None,
            offset=offset if apply_pagination else 0
        )
        
        # Convert CMS data to response models
        people_summaries = []
        for person_data in cms_response.get("data", []):
            # Get primary role (first role if any)
            roles = self.cms_service.get_people_roles(person_data["id"])
            primary_role = roles[0]["role"] if roles else None
            
            # Map faculty code to enum
            faculty_enum = None
            if person_data.get("faculty_enum"):
                for enum in FacultyEnum:
                    if enum.code == person_data["faculty_enum"]:
                        faculty_enum = enum
                        break
            
            person_summary = PersonSummary(
                id=person_data["id"],
                name=person_data["name"],
                first_name=person_data.get("first_name"),
                last_name=person_data.get("last_name"),
                primary_role=primary_role,
                faculty_enum=faculty_enum,
                academic_title=person_data.get("academic_degree")
            )
            people_summaries.append(person_summary)
        
        return PeopleResponse(
            people=people_summaries,
            total_count=cms_response.get("meta", {}).get("filter_count", len(people_summaries)),
            faculty_filter=faculty_filter
        )

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Get detailed information about a specific person from CMS"""
        
        person_data = self.cms_service.get_person_by_id(person_id)
        if not person_data:
            return None
        
        # Get roles and courses
        roles_data = self.cms_service.get_people_roles(person_id)
        courses_data = self.cms_service.get_people_courses(person_id)
        
        # Convert roles
        roles = []
        for role_data in roles_data:
            lsf_role_enum = None
            if role_data.get("lsf_role_enum"):
                try:
                    lsf_role_enum = LSFRoleEnum(role_data["lsf_role_enum"])
                except ValueError:
                    logger.warning(f"Invalid LSFRole enum value: {role_data['lsf_role_enum']}")
            institutions = role_data.get("institutions", [])
            if isinstance(institutions, str):
                institutions = [institutions]
            role = PersonRole(
                lsf_role_enum=lsf_role_enum,
                institutions=institutions
            )
            roles.append(role)
        
        # Convert courses
        courses = []
        for course_data in courses_data:
            course = PersonCourse(
                course_number=course_data.get("course_number"),
                course_name=course_data.get("course_name"),
                semester=course_data.get("semester"),
                course_url=course_data.get("course_url")
            )
            courses.append(course)
        
        # Basic info
        basic_info = PersonBasicInfo(
            first_name=person_data.get("first_name"),
            last_name=person_data.get("last_name"),
            gender=person_data.get("gender"),
            title=person_data.get("title"),
            academic_degree=person_data.get("academic_degree"),
            employment_status=person_data.get("employment_status"),
            name_suffix=person_data.get("name_suffix"),
            status=person_data.get("status"),
            note=person_data.get("note"),
            office_hours=person_data.get("office_hours")
        )
        
        # Map faculty code to enum
        faculty_enum = None
        if person_data.get("faculty_enum"):
            for enum in FacultyEnum:
                if enum.code == person_data["faculty_enum"]:
                    faculty_enum = enum
                    break
        
        return Person(
            id=person_data["id"],
            profile_url=person_data.get("profile_url"),
            name=person_data["name"],
            basic_info=basic_info,
            email=person_data.get("email"),
            address=person_data.get("address"),
            faculty_enum=faculty_enum,
            roles=roles,
            courses=courses
        )

    async def get_available_faculties(self) -> Dict[str, any]:
        """Get list of faculties that have people data from CMS"""
        
        # Get all people to extract faculty information
        all_people = self.cms_service.get_all_people(limit=10000)  # Get all people
        
        faculty_counts = {}
        faculty_names = {}
        
        for person in all_people.get("data", []):
            faculty_enum = person.get("faculty_enum")
            faculty_name = person.get("faculty")
            
            if faculty_enum:
                if faculty_enum not in faculty_counts:
                    faculty_counts[faculty_enum] = 0
                    faculty_names[faculty_enum] = faculty_name
                faculty_counts[faculty_enum] += 1
        
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