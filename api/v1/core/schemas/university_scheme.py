from pydantic import BaseModel

from shared.enums.university_enums import UniversityEnum


class University(BaseModel):
    id: UniversityEnum
    title: str
