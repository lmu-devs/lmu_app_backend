from sqlalchemy.orm import Session

from shared.src.core.logging import get_main_fetcher_logger
from shared.src.enums import UniversityEnum, university_translations
from shared.src.tables import UniversityTable, UniversityTranslationTable


class UniversityService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_main_fetcher_logger(__name__)

    def add_universities(self):
        """Add universities and their translations to database"""
        self.logger.info("⬆️  Adding universities to database...")

        for university in UniversityEnum:
            university_table = UniversityTable(id=university.value)
            self.db.merge(university_table)
            self._add_university_translations(university)

        self.db.commit()
        self.logger.info("💾 Added universities to database")

    def _add_university_translations(self, university):
        translations = university_translations[university]
        for language, title in translations.items():
            translation = UniversityTranslationTable(
                university_id=university.value, language=language.value, title=title
            )
            self.db.merge(translation)
