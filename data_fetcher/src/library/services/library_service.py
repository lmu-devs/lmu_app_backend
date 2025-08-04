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

        # Get or create the main library record
        existing_library = self.db.query(LibraryTable).filter(LibraryTable.id == library.id).first()

        if existing_library:
            # Update existing library fields
            existing_library.hash = library.hash
            existing_library.url = library.url
            existing_library.reservation_url = library.reservation_url

            # Update contact information
            if library.contact:
                existing_library.external_url = library.contact.website.url if library.contact.website else None
                existing_library.email = library.contact.email[0] if library.contact.email else None
                existing_library.phone = library.contact.phone.model_dump() if library.contact.phone else None
            else:
                existing_library.external_url = None
                existing_library.email = None
                existing_library.phone = None
        else:
            # Create new library if it doesn't exist
            external_url = None
            email = None
            phone = None

            if library.contact:
                external_url = library.contact.website.url if library.contact.website else None
                email = library.contact.email[0] if library.contact.email else None
                phone = library.contact.phone.model_dump() if library.contact.phone else None

            existing_library = LibraryTable(
                id=library.id,
                hash=library.hash,
                url=library.url,
                reservation_url=library.reservation_url,
                external_url=external_url,
                email=email,
                phone=phone,
            )
            self.db.add(existing_library)
            self.db.flush()  # Get the ID for foreign keys

        # Update location
        existing_location = (
            self.db.query(LibraryLocationTable).filter(LibraryLocationTable.library_id == library.id).first()
        )

        if library.location:
            if existing_location:
                # Update existing location
                existing_location.address = library.location.address
                existing_location.latitude = library.location.latitude
                existing_location.longitude = library.location.longitude
            else:
                # Create new location
                new_location = LibraryLocationTable(
                    library_id=library.id,
                    address=library.location.address,
                    latitude=library.location.latitude,
                    longitude=library.location.longitude,
                )
                self.db.add(new_location)
        elif existing_location:
            # Remove location if it no longer exists
            self.db.delete(existing_location)

        # Update translations
        services = library.services.model_dump() if library.services else None
        equipment = library.equipment.model_dump() if library.equipment else None

        existing_translation = (
            self.db.query(LibraryTranslationTable)
            .filter(
                LibraryTranslationTable.library_id == library.id,
                LibraryTranslationTable.language == LanguageEnum.GERMAN,
            )
            .first()
        )

        if existing_translation:
            # Update existing translation
            existing_translation.name = library.title
            existing_translation.services = services
            existing_translation.equipment = equipment
            existing_translation.subject_areas = library.subject_areas
        else:
            # Create new translation
            new_translation = LibraryTranslationTable(
                library_id=library.id,
                name=library.title,
                language=LanguageEnum.GERMAN,
                services=services,
                equipment=equipment,
                subject_areas=library.subject_areas,
            )
            self.db.add(new_translation)

        # Update areas - this is more complex due to the relationships
        # Delete existing areas and their related data
        existing_areas = self.db.query(LibraryAreaTable).filter(LibraryAreaTable.library_id == library.id).all()

        for existing_area in existing_areas:
            self.db.delete(existing_area)

        # Create new areas
        if library.areas:
            for area in library.areas:
                # Create opening hours
                opening_hours = []
                if area.opening_hours:
                    for day in area.opening_hours.days:
                        opening_hours.append(
                            LibraryAreaOpeningHoursTable(
                                weekday=day.day,
                                time_ranges=[tr.model_dump(mode="json") for tr in day.time_ranges],
                            )
                        )

                # Create area translation
                area_translation = LibraryAreaTranslationTable(
                    name=area.name,
                    language=LanguageEnum.GERMAN,
                )

                # Create the area
                new_area = LibraryAreaTable(
                    library_id=library.id,
                    opening_hours=opening_hours,
                    translations=[area_translation],
                )
                self.db.add(new_area)

        self.db.commit()
        self.db.refresh(existing_library)
