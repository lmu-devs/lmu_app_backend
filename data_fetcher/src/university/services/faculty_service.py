from sqlalchemy.orm import Session

from shared.src.core.logging import get_main_fetcher_logger
from shared.src.enums import FacultyEnum, faculty_translations
from shared.src.tables import FacultyTable, FacultyTranslationTable


class FacultyService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_main_fetcher_logger(__name__)

    def add_faculties(self):
        """Add faculties and their translations to database"""
        self.logger.info("⬆️  Adding faculties to database...")

        for faculty in FacultyEnum:
            faculty_table = FacultyTable(id=faculty.value)
            self.db.merge(faculty_table)
            self._add_faculty_translations(faculty)

        self.db.commit()
        self.logger.info("💾 Added universities to database")

    def _add_faculty_translations(self, faculty):
        translations = faculty_translations[faculty]
        for language, title in translations.items():
            translation = FacultyTranslationTable(faculty_id=faculty.value, language=language.value, title=title)
            self.db.merge(translation)
