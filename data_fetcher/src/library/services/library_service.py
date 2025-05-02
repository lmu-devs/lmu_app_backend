from sqlalchemy.orm import Session

from data_fetcher.src.library.crawler.library_crawler import LibraryCrawler
from data_fetcher.src.library.models.library_model import Library
from shared.src.core.logging import get_library_logger
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.translation_service import TranslationService
from shared.src.tables.library.library_area_table import (
    LibraryAreaOpeningHoursTable,
    LibraryAreaTable,
    LibraryAreaTranslationTable,
)
from shared.src.tables.library.library_table import (
    LibraryLocationTable,
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

    def _get_library_data(self):
        libraries = self.crawler._parse_libraries_list()
        total = len(libraries)
        for i, library in enumerate(libraries):
            # try:
            logger.info(f"[{i + 1}/{total}] Processing library")
            self.crawler.set_page_hash_id(library["url"])
            has_changed = self.has_library_changed()
            if has_changed:
                logger.info(f"📝 Library {library.get('name')} has changed. Updating...")
                result = self.crawler.get_library(library)
                if result:
                    self._update_library_data(result)
            else:
                logger.info(f"⏭️ Library {library.get('name')} has not changed. Skipping update.")
        # except Exception as e:
        #     logger.error(f"🚨 Error crawling library {library}: {e}")

        logger.info("Munich Library Crawler script finished.")

    def has_library_changed(self) -> bool:
        """
        Check if the content of the library has changed.
        When the content has changed, the library data is updated.
        """
        library_data = self.db.query(LibraryTable).filter(LibraryTable.id == self.crawler.current_id).first()
        if library_data:
            print(library_data.hash, self.crawler.current_hash)
            if library_data.hash == self.crawler.current_hash:
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
        logger.info(f"🔄 Updating library {library.title}")
        # delete all data for this library
        self.db.query(LibraryTable).filter(LibraryTable.id == library.id).delete()
        self.db.flush()

        services = library.services.model_dump() if library.services else None
        print(services)
        equipment = library.equipment.model_dump() if library.equipment else None
        print(equipment)

        translation = LibraryTranslationTable(
            library_id=library.id,
            name=library.title,
            language=LanguageEnum.GERMAN,
            services=services,
            equipment=equipment,
            subject_areas=library.subject_areas,
        )

        areas = []
        if library.areas:
            for area in library.areas:
                opening_hours = []
                if area.opening_hours:
                    for day in area.opening_hours.days:
                        opening_hours.append(
                            LibraryAreaOpeningHoursTable(
                                weekday=day.day,
                                time_ranges=[tr.model_dump(mode="json") for tr in day.time_ranges],
                            )
                        )

                area_translation = LibraryAreaTranslationTable(
                    name=area.name,
                    language=LanguageEnum.GERMAN,
                )
                areas.append(
                    LibraryAreaTable(
                        library_id=library.id,
                        opening_hours=opening_hours,
                        translations=[area_translation],
                    )
                )

        location = None
        if library.location:
            location = LibraryLocationTable(
                library_id=library.id,
                address=library.location.address,
                latitude=library.location.latitude,
                longitude=library.location.longitude,
            )

        images = None
        if library.images:
            images = library.images.model_dump()

        external_url = None
        if library.contact and library.contact.website:
            external_url = library.contact.website.url

        email = None
        if library.contact and library.contact.email:
            email = library.contact.email[0]

        phone = None
        if library.contact and library.contact.phone:
            phone = library.contact.phone.model_dump()

        table = LibraryTable(
            id=library.id,
            hash=library.hash,
            images=images,
            url=library.url,
            reservation_url=library.reservation_url,
            location=location,
            external_url=external_url,
            email=email,
            phone=phone,
            areas=areas,
            translations=[translation],
        )

        self.db.add(table)
        self.db.flush()
        # translations = self.translator.create_missing_translations(table)
        # self.db.add_all(translations)
        self.db.commit()
        self.db.refresh(table)
