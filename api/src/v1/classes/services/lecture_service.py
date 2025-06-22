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
    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_all_lectures(self) -> Lectures:
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = ALL_LECTURE_QERRY_NAME
        query_path = base_path / folder / query_name
        response = self.directus.execute_query_file(
            query_file_path=query_path,
        )
        print("Response from Directus:", response)
        lectures_raw = [tuple(x.values()) for x in response["data"]["lecture"]]
        return Lectures.from_raw(lectures_raw)

    async def get_lectures_from_faculty(
        self, faculty_id: str, db: AsyncSession
    ) -> Lectures:
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = LECTURE_BY_FACULTY_NAME
        query_path = base_path / folder / query_name
        faculty = faculty_translations[FacultyEnum(faculty_id)][LanguageEnum.GERMAN]
        print(faculty)
        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"facultyString": faculty},
        )
        print("Response from Directus:", response)
        print("amount of lectures:", len(response["data"]["lecture"]))
        lectures_raw = [tuple(x.values()) for x in response["data"]["lecture"]]
        return Lectures.from_raw(self.filter_lectures_by_target(lectures_raw, faculty))

    def filter_lectures_by_target(
        self, lectures: List[tuple[str, str, List[List[str]]]], target: str
    ) -> List[tuple[str, str, List[List[str]]]]:
        filtered: list[tuple[str, str, List[List[str]]]] = []
        for lec in lectures:
            print(lec)
            tree_paths = lec[2]
            if not tree_paths:
                continue
            if any(len(item) > 1 and item[1] == target for item in tree_paths):
                filtered.append(lec)
        return filtered

    async def debug_tables(self, db: AsyncSession):
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        result = await db.execute(text(sql))
        tables = result.fetchall()
        print("All tables:", [row[0] for row in tables])

    async def debug_directus_tables(self, db: AsyncSession):
        sql = """
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name = 'lecture' 
            OR table_name LIKE '%lecture%'
        """
        result = await db.execute(text(sql))
        tables = result.fetchall()
        print("Lecture tables:", tables)

    async def find_lecture_in_all_schemas(self, db: AsyncSession):
        sql = """
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE tablename LIKE '%lecture%'
        """
        result = await db.execute(text(sql))
        tables = result.fetchall()
        print("Lecture tables in all schemas:", tables)
