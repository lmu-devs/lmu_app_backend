from pathlib import Path
from typing import List

from api.src.v1.core.flatten_response_util import flatten_response
from shared.src.core.settings import get_settings
from shared.src.tables.lectures import LectureTable, TreePathTable, ClassBaseInfoTable
from shared.src.services.directus_service import DirectusService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    text,
    select,
)


from ..models.lecture import LecturesBasic, LectureBasic
from shared.src.enums.faculty_enums import (
    LanguageEnum,
)

GRAPHQL_FOLDER_NAME = "graphql"
ALL_LECTURE_QERRY_NAME = "all_lectures.graphql"
LECTURE_BY_FACULTY_NAME = "faculty_lectures.graphql"
FACULTY_BY_ID_QUERY_NAME = "faculty_title_by_id.graphql"


class LectureService:
    """Service to interact with lectures in the Directus database."""

    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_all_lectures(self) -> LecturesBasic:
        """Get all lectures."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = ALL_LECTURE_QERRY_NAME
        query_path = base_path / folder / query_name
        response = self.directus.execute_query_file(
            query_file_path=query_path,
        )
        return LecturesBasic.from_directus_dict(response["data"]["lecture"])


    async def get_lectures_from_faculty_db(self, faculty_id: int, db: AsyncSession):
        faculty_title = await self.get_faculty_from_id(faculty_id, LanguageEnum.GERMAN)
        print(f"Faculty Title: {faculty_title}")
        stmt = (
            select(
                LectureTable.publish_id,
                LectureTable.title.label("name"),
                ClassBaseInfoTable.sws,
                ClassBaseInfoTable.class_type,
                ClassBaseInfoTable.language,
                ClassBaseInfoTable.semester
            )
            .join(TreePathTable, TreePathTable.lecture_publish_id == LectureTable.publish_id)
            .join(ClassBaseInfoTable, ClassBaseInfoTable.lecture_publish_id == LectureTable.publish_id)
            .where((TreePathTable.path[2] == faculty_title))
                #& (ClassBaseInfoTable.semester == "SoSe 25"))
        )
        result = await db.execute(stmt)
        rows = result.mappings().all()
        print(rows)
        lecture_models = [LectureBasic.model_validate(row) for row in rows]
        return LecturesBasic(root=lecture_models)

    async def get_lectures_from_faculty(self, faculty_id: int) -> LecturesBasic:
        """Get all lectures from a specified faculty."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = LECTURE_BY_FACULTY_NAME
        query_path = base_path / folder / query_name
        faculty_title = await self.get_faculty_from_id(faculty_id, LanguageEnum.GERMAN)
        print(f"Faculty Title: {faculty_title}")

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"facultyString": faculty_title},
        )

        return LecturesBasic.from_directus_dict(response["data"]["lecture"])

    async def get_faculty_from_id(self, faculty_id: int, language: LanguageEnum) -> str:
        """Get the faculty title from its ID using directus."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = FACULTY_BY_ID_QUERY_NAME
        query_path = base_path / folder / query_name
        variables = {"facultyID": str(faculty_id), "languageCode": language.value}

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=variables,
        )
        if not (faculties := response["data"]["faculties_translations"]):
            raise ValueError(f"No faculty found with ID {faculty_id} in language {language.value}")

        return faculties[0]["title"]
