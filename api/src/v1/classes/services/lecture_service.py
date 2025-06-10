from typing import List
from pathlib import Path

from api.src.v1.core.flatten_response_util import flatten_response
from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService

from ..models.lecture import Lectures

GRAPHQL_FOLDER_NAME = "graphql"
FACULTY_QUERY_NAME = "faculty_query.graphql"
UNIVERSITY_QUERY_NAME = "university_query.graphql"


class LectureService:
    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_lectures(self) -> Lectures:
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = FACULTY_QUERY_NAME
        query_path = base_path / folder / query_name
        """
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"languageCode": self.language_code},
        )
        """
        return Lectures()
