from pathlib import Path
from typing import List

from api.src.v1.core.flatten_response_util import flatten_response
from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


from ..models.lecture import Lectures
from shared.src.enums.faculty_enums import (
    FacultyEnum,
    faculty_translations,
    LanguageEnum,
)

GRAPHQL_FOLDER_NAME = "graphql"
ALL_LECTURE_QERRY_NAME = "all_lectures.graphql"
LECTURE_BY_FACULTY_NAME = "faculty_lectures.graphql"


class LectureService:
    """Service to interact with lectures in the Directus database."""

    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_all_lectures(self) -> Lectures:
        """Get all lectures."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = ALL_LECTURE_QERRY_NAME
        query_path = base_path / folder / query_name
        response = self.directus.execute_query_file(
            query_file_path=query_path,
        )
        return Lectures.from_directus_dict(response["data"]["lecture"])

    async def get_lectures_from_faculty(self, facutlty_id: int) -> Lectures:
        """Get all lectures from a specified faculty."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = LECTURE_BY_FACULTY_NAME
        query_path = base_path / folder / query_name
        faculty_enum = self.get_faculty_from_id(facutlty_id)
        faculty = faculty_translations[faculty_enum][LanguageEnum.GERMAN]
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"facultyString": faculty},
        )
        print(len(response["data"]["lecture"]))
        return Lectures.from_directus_dict(response["data"]["lecture"])

    def get_faculty_from_id(self, faculty_id: int) -> FacultyEnum:
        """Get the faculty enum from its ID."""
        faculty_mapping = {
            1: FacultyEnum.CATHOLIC_THEOLOGY,
            2: FacultyEnum.PROTESTANT_THEOLOGY,
            3: FacultyEnum.LAW,
            4: FacultyEnum.BUSINESS_ADMIN,
            5: FacultyEnum.ECONOMICS,
            7: FacultyEnum.MEDICINE,
            8: FacultyEnum.VETERINARY_MEDICINE,
            9: FacultyEnum.HISTORY_ARTS,
            10: FacultyEnum.PHILOSOPHY,
            11: FacultyEnum.PSYCHOLOGY_EDUCATION,
            12: FacultyEnum.CULTURE_STUDIES,
            13: FacultyEnum.LANGUAGES_LITERATURE,
            15: FacultyEnum.SOCIAL_SCIENCES,
            16: FacultyEnum.MATH_INFO_STATS,
            17: FacultyEnum.PHYSICS,
            18: FacultyEnum.CHEMISTRY_PHARMACY,
            19: FacultyEnum.BIOLOGY,
            20: FacultyEnum.GEOSCIENCES,
        }
        return faculty_mapping[faculty_id]