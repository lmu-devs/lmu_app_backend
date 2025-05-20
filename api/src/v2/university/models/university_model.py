from pydantic import BaseModel

from shared.src.enums import UniversityEnum

from .faculty_model import Faculties


class University(BaseModel):
    id: UniversityEnum
    title: str
    faculties: Faculties | None = None
