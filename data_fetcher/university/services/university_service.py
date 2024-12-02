from sqlalchemy.orm import Session

from shared.enums.university_enums import University, university_translations
from shared.tables.university_table import UniversityTable, UniversityTranslationTable

def add_university_to_database(db : Session):
    for university in University:
        university_table = UniversityTable(id=university.value)
        db.merge(university_table)
        _add_university_translations_to_database(db, university)
    
    db.commit()

def _add_university_translations_to_database(db, university):
    translations = university_translations[university]
    for language, title in translations.items():
        translation = UniversityTranslationTable(
            university_id=university.value,
            language=language.value,
            title=title
        )
        db.merge(translation) 