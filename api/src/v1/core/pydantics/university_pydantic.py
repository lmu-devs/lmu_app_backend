from shared.src.enums import UniversityEnum
from shared.src.tables import UniversityTable, UniversityTranslationTable

from ..schemas import University


def university_to_pydantic(university: UniversityTable) -> University:
    translation: UniversityTranslationTable = university.translations[0] if university.translations else "Not translated"
    return University(
        id=UniversityEnum(university.id),
        title=translation.title,
    )