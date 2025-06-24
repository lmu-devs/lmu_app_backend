from pydantic import BaseModel, RootModel
from typing import List

from shared.src.enums import UniversityEnum


class University(BaseModel):
    id: UniversityEnum
    name: str


class Universities(RootModel):
    root: List[University] | list = []
