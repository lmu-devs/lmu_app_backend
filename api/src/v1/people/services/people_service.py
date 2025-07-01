from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, distinct

from shared.src.core.logging import get_main_fetcher_logger
from shared.src.tables.people.people_table import PeopleTable, PeopleRoleTable, PeopleCoursesTable
from shared.src.tables.faculty_table import FacultyTable, FacultyTranslationTable
from shared.src.enums import FacultyEnum, AcademicTitle, LSFRole, map_faculty_name_to_enum, LanguageEnum
from ..models.people_model import (
    Person, PersonSummary, PeopleResponse, PersonRole, PersonCourse, PersonBasicInfo
)

logger = get_main_fetcher_logger(__name__)


class PeopleService:
    def __init__(self, db: Session):
        self.db = db

    def _get_faculty_name_by_id(self, faculty_id: str) -> Optional[str]:
        """Get German faculty name by faculty code from database."""
        try:
            translation = self.db.query(FacultyTranslationTable).filter(
                FacultyTranslationTable.faculty_id == faculty_id,  # Use code directly
                FacultyTranslationTable.language == LanguageEnum.GERMAN.value
            ).first()
            return translation.title if translation else None
        except Exception as e:
            logger.warning(f"Could not find faculty name for code {faculty_id}: {e}")
            return None

    def get_faculty_enum_by_id(self, faculty_id: str) -> Optional[FacultyEnum]:
        """Get faculty enum from faculty code."""
        try:
            translation = self.db.query(FacultyTranslationTable).filter(
                FacultyTranslationTable.faculty_id == faculty_id,  # Use code directly
                FacultyTranslationTable.language == LanguageEnum.GERMAN.value
            ).first()
            if translation and translation.title:
                return map_faculty_name_to_enum(translation.title)
            return None
        except Exception as e:
            logger.warning(f"Could not find faculty enum for code {faculty_id}: {e}")
            return None

    async def get_people(
        self,
        faculty_filter: Optional[FacultyEnum] = None,
        faculty_id_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        apply_pagination: bool = True
    ) -> PeopleResponse:
        """Get list of people with optional faculty filter and conditional pagination"""
        query = self.db.query(PeopleTable).options(
            joinedload(PeopleTable.roles),
            joinedload(PeopleTable.courses)
        )
        applied_faculty_filter = None
        if faculty_filter:
            from shared.src.enums.faculty_enums import faculty_translations
            german_faculty_name = faculty_translations.get(faculty_filter, {}).get(LanguageEnum.GERMAN)
            if german_faculty_name:
                query = query.filter(PeopleTable.faculty == german_faculty_name)
                applied_faculty_filter = faculty_filter
        elif faculty_id_filter:
            german_faculty_name = self._get_faculty_name_by_id(faculty_id_filter)
            if not german_faculty_name:
                logger.warning(f"No German faculty name found for code {faculty_id_filter}")
                return PeopleResponse(people=[], total_count=0, faculty_filter=None)
            query = query.filter(PeopleTable.faculty == german_faculty_name)
            applied_faculty_filter = None
            for enum in FacultyEnum:
                if enum.code == faculty_id_filter:
                    applied_faculty_filter = enum
                    break
        total_count = query.count()
        if apply_pagination:
            people_data = query.offset(offset).limit(limit).all()
        else:
            people_data = query.all()
        people_summaries = []
        for person_db in people_data:
            primary_role = None
            if person_db.roles:
                primary_role = person_db.roles[0].role
            faculty_enum = None
            faculty_code = None
            if person_db.faculty:
                faculty_enum = map_faculty_name_to_enum(person_db.faculty)
                if faculty_enum:
                    faculty_code = faculty_enum.code
                else:
                    try:
                        faculty_translation = self.db.query(FacultyTranslationTable).filter(
                            FacultyTranslationTable.title == person_db.faculty,
                            FacultyTranslationTable.language == LanguageEnum.GERMAN.value
                        ).first()
                        if faculty_translation:
                            faculty_code = faculty_translation.faculty_id
                    except Exception:
                        pass
            person_summary = PersonSummary(
                id=person_db.id,
                name=person_db.name,
                first_name=person_db.first_name,
                last_name=person_db.last_name,
                primary_role=primary_role,
                faculty_enum=faculty_enum,
                academic_title=person_db.academic_degree
            )
            people_summaries.append(person_summary)
        return PeopleResponse(
            people=people_summaries,
            total_count=total_count,
            faculty_filter=applied_faculty_filter
        )

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Get detailed information about a specific person"""
        
        person_db = self.db.query(PeopleTable).options(
            joinedload(PeopleTable.roles),
            joinedload(PeopleTable.courses)
        ).filter(PeopleTable.id == person_id).first()
        
        if not person_db:
            return None
        
        # Convert roles
        roles = []
        for role_db in person_db.roles:
            lsf_role_enum = None
            if role_db.lsf_role_name:
                lsf_role_enum = LSFRole.from_string(role_db.lsf_role_name)
            
            role = PersonRole(
                institution=role_db.institution,
                role=role_db.role,
                institution_url=role_db.institution_url,
                lsf_role_id=role_db.lsf_role_id,
                lsf_role_name=role_db.lsf_role_name,
                lsf_role_enum=lsf_role_enum
            )
            roles.append(role)
        
        # Convert courses
        courses = []
        for course_db in person_db.courses:
            course = PersonCourse(
                course_number=course_db.course_number,
                course_name=course_db.course_name,
                semester=course_db.semester,
                course_url=course_db.course_url
            )
            courses.append(course)
        
        # Basic info
        basic_info = PersonBasicInfo(
            first_name=person_db.first_name,
            last_name=person_db.last_name,
            gender=person_db.gender,
            title=person_db.title,
            academic_degree=person_db.academic_degree,
            employment_status=person_db.employment_status,
            name_suffix=person_db.name_suffix,
            status=person_db.status,
            note=person_db.note,
            office_hours=person_db.office_hours
        )
        
        # Map faculty name to enum and get faculty ID
        faculty_enum = None
        faculty_id = None
        if person_db.faculty:
            faculty_enum = map_faculty_name_to_enum(person_db.faculty)
            # Get faculty ID from enum if possible
            if faculty_enum:
                faculty_id = faculty_enum.id
            else:
                # fallback: get faculty ID from database
                try:
                    faculty_translation = self.db.query(FacultyTranslationTable).filter(
                        FacultyTranslationTable.title == person_db.faculty,
                        FacultyTranslationTable.language == LanguageEnum.GERMAN.value
                    ).first()
                    if faculty_translation:
                        faculty_id = faculty_translation.faculty_id
                except Exception:
                    pass
        
        # Map academic title
        academic_title_enum = None
        if person_db.academic_degree:
            academic_title_enum = AcademicTitle.from_string(person_db.academic_degree)
        
        return Person(
            id=person_db.id,
            profile_url=person_db.profile_url,
            name=person_db.name,
            basic_info=basic_info,
            email=person_db.email,
            address=person_db.address,
            faculty=person_db.faculty,
            faculty_id=faculty_id,
            faculty_enum=faculty_enum,
            academic_title_enum=academic_title_enum,
            roles=roles,
            courses=courses
        )

    async def get_available_faculties(self) -> Dict[str, any]:
        """Get list of faculties that have people data"""
        
        # Query distinct faculty names from people table
        faculty_names = self.db.query(distinct(PeopleTable.faculty)).filter(
            PeopleTable.faculty.isnot(None)
        ).all()
        
        faculties = []
        for (faculty_name,) in faculty_names:
            faculty_enum = map_faculty_name_to_enum(faculty_name)
            
            # Count people in this faculty
            count = self.db.query(func.count(PeopleTable.id)).filter(
                PeopleTable.faculty == faculty_name
            ).scalar()
            
            # Try to get faculty ID from database
            faculty_id = None
            try:
                faculty_translation = self.db.query(FacultyTranslationTable).filter(
                    FacultyTranslationTable.title == faculty_name,
                    FacultyTranslationTable.language == LanguageEnum.GERMAN.value
                ).first()
                if faculty_translation:
                    faculty_id = faculty_translation.faculty_id
            except Exception:
                pass
            
            faculty_info = {
                "id": faculty_id,
                "name": faculty_name,
                "enum": faculty_enum.value if faculty_enum else None,
                "people_count": count
            }
            faculties.append(faculty_info)
        
        # Sort by name
        faculties.sort(key=lambda x: x["name"])
        
        return {
            "faculties": faculties,
            "total_faculties": len(faculties)
        }