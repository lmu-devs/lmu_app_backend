from pathlib import Path
from typing import Optional
from shared.src.core.settings import get_settings
from shared.src.tables.lectures import PersonTable, ClassSessionTable, LectureTable, TreePathTable, ClassBaseInfoTable, AdditionInformationTable, lecture_persons_table
from shared.src.services.directus_service import DirectusService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select
)

from lxml import html

from ..models.lecture import LectureDetails, LecturesBasic, LectureBasic, ClassSession, Person
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

    async def get_lecture_details_db(self, session: AsyncSession, publish_id: int) -> LectureDetails:
        stmt = (
            select(LectureTable)
            .where(LectureTable.publish_id == publish_id)
        ).distinct()

        result = await session.execute(stmt)
        lecture = result.scalar_one_or_none()

        if not lecture:
            raise ValueError(f"Lecture with publish_id {publish_id} not found")

        columns = [
            col for col in AdditionInformationTable.__table__.c
            if col.name != "id"
        ]

        base_stmt = (
            select(*columns)
            .where(AdditionInformationTable.lecture_publish_id == publish_id)
        ).distinct()
        base_result = await session.execute(base_stmt)
        base_row = base_result.mappings().one_or_none()

        sessions_stmt = (
            select(ClassSessionTable)
            .where(ClassSessionTable.lecture_publish_id == publish_id)
        ).distinct()

        sessions_result = await session.execute(sessions_stmt)
        sessions = sessions_result.scalars().all()

        persons_stmt = (
            select(
                PersonTable.first_name,
                PersonTable.surname,
                PersonTable.title
            )
            .join(lecture_persons_table, PersonTable.id == lecture_persons_table.c.person_id)
            .where(lecture_persons_table.c.lecture_publish_id == publish_id)
            .distinct()
        )

        result = await session.execute(persons_stmt)
        persons = result.mappings().all()

        return LectureDetails(
            last_updated=lecture.last_updated,
            persons=[Person.model_validate(person) for person in persons],
            sessions=[ClassSession.model_validate(session.__dict__) for session in sessions],
            addtional_information=self.convert_additional_info_to_markdown(base_row)
        )

    def html_to_text(self, html_str: str) -> str:
        if not html_str:
            return ""
        try:
            tree = html.fromstring(html_str)
            return tree.text_content().strip()
        except Exception:
            return html_str.strip()

    def convert_additional_info_to_markdown(self, add_info: Optional[AdditionInformationTable]) -> str:
        if not add_info:
            return ""

        field_translations = {
            "remark": "Bemerkung",
            "literature": "Literatur",
            "date": "Datum",
            "registration": "Anmeldung",
            "format": "Format",
            "content": "Inhalt",
            "learning_content": "Lerninhalte",
            "target_group": "Zielgruppe",
            "location": "Ort",
            "comment": "Kommentar",
            "assessment": "Leistungsnachweis",
            "time": "Zeit",
            "topic": "Thema",
            "short_comment": "Kurzkommentar",
            "prerequisites": "Voraussetzungen",
            "number": "Nummer",
            "type": "Typ"
        }

        markdown_parts = []
        for field, translation in field_translations.items():
            value = getattr(add_info, field)
            text = self.html_to_text(value)
            if text:
                markdown_parts.append(f"### {translation.title()}\n\n{text}")

        return "\n\n".join(markdown_parts)

    async def get_lectures_from_faculty_db(self, session: AsyncSession, faculty_id: int, year: int, semester_id: int):
        """Get all lectures from a specific faculty, semester and year."""
        faculty_title = await self.get_faculty_from_id(faculty_id, LanguageEnum.GERMAN)
        year_suffix = year % 2000
        semester_prefix = "SoSe" if semester_id == 1 else "WiSe"
        semester_text = (
            f"{semester_prefix} 20{year_suffix}" if semester_id == 1
            else f"{semester_prefix} {year_suffix}{year_suffix + 1}"
        )
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
            .where(
                (TreePathTable.path[2] == faculty_title)
                & (ClassBaseInfoTable.semester == semester_text)
            )
        ).distinct()
        result = await session.execute(stmt)
        rows = result.mappings().all()
        lecture_models = [LectureBasic.model_validate(row) for row in rows]
        return LecturesBasic(root=lecture_models)

    async def get_lectures_from_faculty(self, faculty_id: int) -> LecturesBasic:
        """Get all lectures from a specified faculty."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = LECTURE_BY_FACULTY_NAME
        query_path = base_path / folder / query_name
        faculty_title = await self.get_faculty_from_id(faculty_id, LanguageEnum.GERMAN)

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
