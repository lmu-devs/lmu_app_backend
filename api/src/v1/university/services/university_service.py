from typing import Any
from pathlib import Path

from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService
from ..models.faculty_model import Faculty
from ..models.faculty_model import Faculties
from ..models.university_model import Universities
from ..models.university_model import University
from ..models.university_model import UniversityEnum


GRAPHQL_FOLDER_NAME = "graphql"
FACULTY_QUERY_NAME = "faculty_query.graphql"
UNIVERSITY_QUERY_NAME = "university_query.graphql"


class UniversityService:
    """Service to interact with university data from Directus."""

    def __init__(self, language_code: str):
        self.settings = get_settings()
        self.directus = DirectusService()
        self.language_code = language_code

    async def get_faculties(self) -> Faculties:
        """Fetches faculty id and title from Directus."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = FACULTY_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"languageCode": self.language_code},
        )

        faculties_raw: list[dict[str, Any]] = response["data"]["faculties_translations"]

        return Faculties(
            root=[Faculty(id=int(f["faculties_id"]["id"]), name=f["title"]) for f in faculties_raw]
        )

    async def get_universities(self) -> Universities:
        """Fetches university abbreviation and title from Directus."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = UNIVERSITY_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"languageCode": self.language_code},
        )

        universities_raw: list[dict[str, Any]] = response["data"]["universities_translations"]

        return Universities(
            root=[
                University(
                    id=UniversityEnum(u["universities_id"]["abbreviation"]),
                    name=u["title"],
                )
                for u in universities_raw
            ]
        )
