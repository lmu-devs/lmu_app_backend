from typing import List

from sqlalchemy.orm import Session

from data_fetcher.src.library.crawler.library_crawler import LibraryCrawler
from data_fetcher.src.library.models.library_model import Library
from shared.src.core.logging import get_library_logger
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.translation_service import TranslationService
from shared.src.tables.library.library_table import (
    LibraryOpeningHoursTable,
    LibraryTable,
    LibraryTranslationTable,
)

logger = get_library_logger(__name__)


class LibraryService:
    def __init__(self, db: Session):
        self.db = db
        self.crawler = LibraryCrawler()
        self.translator = TranslationService()

    def run(self):
        self._get_library_data()

    def check_if_content_changed(self, library: Library):
        library_data = self.db.query(LibraryTable).filter(LibraryTable.id == library.id).first()
        if library_data:
            if library_data.hash == library.hash:
                return False
        return True

    # def generate_translation(self, library: Library):
    #     text_with_link_title = self.translator.create_missing_translations(library.services.title, "de")

    #     translation = LibraryTranslationTable(
    #         library_id=library.id,
    #         name=library.name,
    #         services=library.services,
    #         equipment=library.equipment,
    #         subject_areas=library.subject_areas,
    #     )

    def _update_library_data(self, library: Library):
        if not self.check_if_content_changed(library):
            return

        translation = LibraryTranslationTable(
            library_id=library.id,
            name=library.name,
            language=LanguageEnum.GERMAN,
            services=library.services,
            equipment=library.equipment,
            subject_areas=library.subject_areas,
        )

        opening_hours = []
        for day in library.opening_hours.days:
            opening_hours.append(
                LibraryOpeningHoursTable(
                    weekday=day.day,
                    time_ranges=day.time_ranges,
                )
            )

        table = LibraryTable(
            id=library.id,
            name=library.name,
            hash=library.hash,
            images=library.images,
            url=library.url,
            reservation_url=library.reservation_url,
            location=library.location,
            contact=library.contact,
            opening_hours=opening_hours,
            services=library.services,
            equipment=library.equipment,
            subject_areas=library.subject_areas,
            translation=translation,
        )

        self.db.add(table)
        self.db.flush()
        # translations = self.translator.create_missing_translations(table)
        # self.db.add_all(translations)
        self.db.commit()
        self.db.refresh(table)

    def _get_library_data(self):
        libraries = self.crawler._parse_libraries_list()
        libraries_data: List[Library] = []
        total = len(libraries)
        for i, library in enumerate(libraries):
            logger.info(f"[{i + 1}/{total}] Processing library")
            result = self.crawler.get_library(library)
            if result:
                self._update_library_data(result)

        if libraries_data:
            logger.info(f"Successfully crawled {len(libraries_data)} library entries.")
        else:
            logger.error("Crawling returned no library data. File not saved.")

        logger.info("Munich Library Crawler script finished.")
