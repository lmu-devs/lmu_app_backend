from typing import List
from pathlib import Path

from api.src.v1.core.flatten_response_util import flatten_response
from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService
from ..models.faculty_model import FacultyEnum
from ..models.faculty_model import Faculty
from ..models.faculty_model import Faculties
from ..models.university_model import Universities
from ..models.university_model import University
from ..models.university_model import UniversityEnum


GRAPHQL_FOLDER_NAME = "graphql"
FACULTY_QUERY_NAME = "faculty_query.graphql"
UNIVERSITY_QUERY_NAME = "university_query.graphql"


class UniversityService:
    def __init__(self, language_code: str):
        self.settings = get_settings()
        self.directus = DirectusService()
        self.language_code = language_code

    async def get_faculties(self) -> Faculties:
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = FACULTY_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"languageCode": self.language_code},
        )

        faculties_raw = flatten_response(response)
        return Faculties(
            root=[
                Faculty(id=FacultyEnum(f["faculties_id"]["id"]), title=f["title"])
                for f in faculties_raw["faculties_translations"]
            ]
        )

    async def get_universities(self) -> Universities:
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = UNIVERSITY_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"languageCode": self.language_code},
        )
        universities_raw = flatten_response(response)
        return Universities(
            root=[
                University(
                    id=UniversityEnum(u["universities_id"]["abbreviation"]),
                    title=u["title"],
                )
                for u in universities_raw["universities_translations"]
            ]
        )
