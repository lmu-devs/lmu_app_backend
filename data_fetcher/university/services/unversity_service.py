from shared.enums.university_enums import (UniversityEnum,
                                           university_translations)
from shared.tables.university_table import (UniversityTable,
                                            UniversityTranslationTable)

# add university to database
# add university translations to database
# add university movies to database

async def add_university_to_database(db):
    for university in UniversityEnum:
        university_table = UniversityTable(id=university)
        await _add_university_translations_to_database(db, university)
        db.add(university_table)
    db.commit()

async def _add_university_translations_to_database(db, university):
    for language in university_translations:
            university_translation_table = UniversityTranslationTable(university=university, language=language)