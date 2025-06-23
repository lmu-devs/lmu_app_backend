from pydantic import BaseModel, RootModel
from typing import List

from shared.src.enums import UniversityEnum
from shared.src.tables import UniversityTable, UniversityTranslationTable


class University(BaseModel):
    id: UniversityEnum
    title: str


class Universities(RootModel):
    root: List[University] | list = []
