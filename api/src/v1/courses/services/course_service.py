from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.settings import get_settings
from shared.src.enums.faculty_enums import LanguageEnum
from shared.src.models.location_model import Location
from shared.src.services.directus_service import DirectusService
from shared.src.tables.courses.course_tables import (
    CourseAdditionInformationTable,
    CourseAssociatedProgramTable,
    CourseBaseInfoTable,
    CoursePersonTable,
    CourseSessionTable,
    CourseTable,
    CourseTreePathTable,
    course_persons_association,
)
from shared.src.tables.roomfinder.building_table import BuildingLocationTable
from shared.src.tables.roomfinder.room_table import RoomTable

from ..models.course import CourseBasic, CourseDetails, CoursesBasic, Person, Session

FACULTY_BY_ID_QUERY_NAME = "faculty_title_by_id.graphql"
GRAPHQL_FOLDER_NAME = "graphql"


class CourseService:
    """Service to interact with courses in the Directus database."""

    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def getcourse_details_db(self, session: AsyncSession, publish_id: int) -> CourseDetails:
        stmt = (select(CourseTable).where(CourseTable.publish_id == publish_id)).distinct()

        result = await session.execute(stmt)
        course = result.scalar_one_or_none()

        if not course:
            raise ValueError(f"Course with publish_id {publish_id} not found")

        columns = [col for col in CourseAdditionInformationTable.__table__.c if col.name != "id"]

        base_stmt = (select(*columns).where(CourseAdditionInformationTable.course_publish_id == publish_id)).distinct()
        base_result = await session.execute(base_stmt)
        base_row = base_result.mappings().one_or_none()

        # Select session columns + room name + building location via LEFT JOINs
        sessions_stmt = (
            select(
                *CourseSessionTable.__table__.c,
                RoomTable.name.label("room_name"),
                BuildingLocationTable.address,
                BuildingLocationTable.latitude,
                BuildingLocationTable.longitude,
            )
            .outerjoin(RoomTable, CourseSessionTable.room_id == RoomTable.id)
            .outerjoin(
                BuildingLocationTable,
                CourseSessionTable.building_id == BuildingLocationTable.building_id,
            )
            .where(CourseSessionTable.course_publish_id == publish_id)
        ).distinct()

        sessions_result = await session.execute(sessions_stmt)
        sessions_rows = sessions_result.mappings().all()

        persons_stmt = (
            select(
                CoursePersonTable.first_name,
                CoursePersonTable.surname,
                CoursePersonTable.title,
            )
            .join(
                course_persons_association,
                CoursePersonTable.id == course_persons_association.c.person_id,
            )
            .where(course_persons_association.c.course_publish_id == publish_id)
            .distinct()
        )

        result = await session.execute(persons_stmt)
        persons = result.mappings().all()

        return CourseDetails(
            last_updated=course.last_updated,
            persons=[Person.model_validate(person) for person in persons],
            sessions=[self._create_session_from_row(dict(row)) for row in sessions_rows],
            additional_information=self.convert_additional_info_to_markdown(base_row),
        )

    def _create_session_from_row(self, row: dict) -> Session:
        """Create a Session API model from a database row dict."""
        address = row.pop("address", None)
        latitude = row.pop("latitude", None)
        longitude = row.pop("longitude", None)
        room_name = row.pop("room_name", None)

        location = Location(address=address, latitude=latitude, longitude=longitude) if address else None

        return Session.from_table(row, room_name=room_name, location=location)

    def convert_additional_info_to_markdown(self, add_info: Optional[CourseAdditionInformationTable]) -> str:
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
            "type": "Typ",
        }

        markdown_parts = []
        for field, translation in field_translations.items():
            value = getattr(add_info, field)
            text = value if value else ""
            if text:
                markdown_parts.append(f"### {translation.title()}\n\n{text}")

        return "\n\n".join(markdown_parts)

    async def get_courses_from_faculty_db(self, session: AsyncSession, faculty_id: int, year: int, semester_id: int):
        """Get all classes from a specific faculty, semester and year."""
        faculty_title = await self.get_faculty_from_id(faculty_id, LanguageEnum.GERMAN)
        year_suffix = year % 2000
        semester_prefix = "SoSe" if semester_id == 1 else "WiSe"
        semester_text = (
            f"{semester_prefix} 20{year_suffix}"
            if semester_id == 1
            else f"{semester_prefix} {year_suffix}{year_suffix + 1}"
        )
        stmt = (
            select(
                CourseTable.publish_id,
                CourseTable.title.label("name"),
                CourseBaseInfoTable.sws,
                CourseBaseInfoTable.type,
                CourseBaseInfoTable.language,
                CourseBaseInfoTable.semester,
                CourseAssociatedProgramTable.degree,
            )
            .join(
                CourseTreePathTable,
                CourseTreePathTable.course_publish_id == CourseTable.publish_id,
            )
            .join(
                CourseAssociatedProgramTable,
                CourseAssociatedProgramTable.course_publish_id == CourseTable.publish_id,
            )
            .join(
                CourseBaseInfoTable,
                CourseBaseInfoTable.course_publish_id == CourseTable.publish_id,
            )
            .where((CourseTreePathTable.path[2] == faculty_title) & (CourseBaseInfoTable.semester == semester_text))
        ).distinct()
        result = await session.execute(stmt)
        rows = result.mappings().all()
        course_models = [CourseBasic.model_validate(row) for row in rows]
        return CoursesBasic(root=course_models)

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
