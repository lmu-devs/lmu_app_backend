from sqlalchemy.orm import Session

from shared.src.core.logging import get_main_fetcher_logger
from shared.src.enums import UniversityEnum, university_translations
from shared.src.tables import UniversityTable, UniversityTranslationTable

logger = get_main_fetcher_logger(__name__)

def add_university_to_database(db : Session):
    logger.info("Adding universities to database...")
    for university in UniversityEnum:
        university_table = UniversityTable(id=university.value)
        db.merge(university_table)
        _add_university_translations_to_database(db, university)
    
    db.commit()
    logger.info("Successfully added universities to database")
def _add_university_translations_to_database(db, university):
    translations = university_translations[university]
    for language, title in translations.items():
        translation = UniversityTranslationTable(
            university_id=university.value,
            language=language.value,
            title=title
        )
        db.merge(translation) 