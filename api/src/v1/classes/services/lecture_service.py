from typing import List
from pathlib import Path

from api.src.v1.core.flatten_response_util import flatten_response
from shared.src.core.settings import get_settings
from shared.src.services.directus_service import DirectusService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


from ..models.lecture import Lectures
from shared.src.enums.faculty_enums import FacultyEnum

GRAPHQL_FOLDER_NAME = "graphql"
ALL_LECTURE_QERRY_NAME = "all_lectures.graphql"


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
        lectures_raw = [tuple(x.values()) for x in response["data"]["lecture"]]
        return Lectures.from_raw(lectures_raw)

    async def get_lectures_from_faculty(
        self, faculty_id: str, db: AsyncSession
    ) -> Lectures:
        sql = """
            SELECT * FROM lecture WHERE jsonb_path_exists(
                tree_paths, 
                '$[*] ? (@[0] == $target || @[1] == $target)'
            )
        """
        await self.debug_tables(db)
        await self.debug_directus_tables(db)
        await self.find_lecture_in_all_schemas(db)
        # result = await db.execute(text(sql), {"target": faculty_id})
        # rows = result.fetchall()
        # print(rows)
        return Lectures()

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
