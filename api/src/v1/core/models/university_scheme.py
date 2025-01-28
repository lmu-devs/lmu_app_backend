from pydantic import BaseModel

from shared.src.tables import UniversityTable, UniversityTranslationTable
from shared.src.enums import UniversityEnum


class University(BaseModel):
    id: UniversityEnum
    title: str
    
    @classmethod
    def from_table(cls, university: UniversityTable) -> 'University':
        translation: UniversityTranslationTable = university.translations[0] if university.translations else "Not translated"
        
        return University(
            id=UniversityEnum(university.id),
            title=translation.title,
        )