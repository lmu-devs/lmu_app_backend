from pydantic import BaseModel

from shared.src.enums import UniversityEnum


class University(BaseModel):
    id: UniversityEnum
    title: str
