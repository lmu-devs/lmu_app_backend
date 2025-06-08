from pydantic import BaseModel, RootModel
from typing import List

from shared.src.enums import UniversityEnum
from shared.src.tables import UniversityTable, UniversityTranslationTable


class University(BaseModel):
    id: UniversityEnum
    title: str

    @classmethod
    def from_table(cls, university: UniversityTable) -> "University":
        translation: UniversityTranslationTable = (
            university.translations[0] if university.translations else "Not translated"
        )

        return University(
            id=UniversityEnum(university.id),
            title=translation.title,
        )


class Universities(RootModel):
    root: List[University] | list = []
