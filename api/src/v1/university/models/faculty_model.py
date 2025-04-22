from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums import FacultyEnum
from shared.src.tables import FacultyTable, FacultyTranslationTable


class Faculty(BaseModel):
    id: FacultyEnum
    title: str

    @classmethod
    def from_table(cls, faculty: FacultyTable) -> "Faculty":
        translation: FacultyTranslationTable = faculty.translations[0] if faculty.translations else "Not translated"

        return Faculty(
            id=FacultyEnum(faculty.id),
            title=translation.title,
        )


class Faculties(RootModel):
    root: List[Faculty] | list = []
