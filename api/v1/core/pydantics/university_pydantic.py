from shared.enums.university_enums import UniversityEnum
from shared.tables.university_table import (UniversityTable,
                                            UniversityTranslationTable)

from ..schemas import University


def university_to_pydantic(university: UniversityTable) -> University:
    translation: UniversityTranslationTable = university.translations[0]
    print(translation.title)
    print(university.id)
    print(UniversityEnum(university.id))
    return University(
        id=UniversityEnum(university.id),
        title=translation.title,
    )