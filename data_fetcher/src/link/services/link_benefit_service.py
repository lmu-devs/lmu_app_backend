from sqlalchemy.orm import Session

from data_fetcher.src.core.services.alias_generation_service import (
    AliasGenerationService,
)
from data_fetcher.src.core.services.favicon_service import FaviconService
from data_fetcher.src.link.constants.link_benefit_constants import (
    link_benefit_constants,
)
from shared.src.core.logging import get_translation_logger
from shared.src.services.translation_service import TranslationService
from shared.src.tables.link.link_benefits_table import (
    LinkBenefitTable,
    LinkBenefitTranslationTable,
)

logger = get_translation_logger(__name__)


class LinkBenefitService:
    def __init__(self, db: Session):
        self.db = db
        self.link_benefit_constants = link_benefit_constants
        self.translation_service = TranslationService()
        self.alias_generation_service = AliasGenerationService()
        self.favicon_service = FaviconService()

    def run(self):
        self._merge_benefits_in_db()
        self._add_missing_aliases()
        self._add_missing_translations()
        self._add_missing_favicon_urls()

    def _delete_benefits_not_in_constants(self):
        # Get the set of link IDs from constants
        constant_benefit_ids = {benefit.id for benefit in self.link_benefit_constants}

        # First delete translations for links that aren't in constants
        self.db.query(LinkBenefitTranslationTable).filter(
            ~LinkBenefitTranslationTable.link_id.in_(constant_benefit_ids)
        ).delete(synchronize_session=False)

        # Then delete the links that aren't in constants
        self.db.query(LinkBenefitTable).filter(~LinkBenefitTable.id.in_(constant_benefit_ids)).delete(
            synchronize_session=False
        )

    def _merge_benefits_in_db(self):
        self._delete_benefits_not_in_constants()

        # Merge the links from constants
        for benefit in self.link_benefit_constants:
            base_benefit = LinkBenefitTable(
                id=benefit.id,
                url=benefit.url,
                image_url=benefit.image_url,
            )
            self.db.merge(base_benefit)

        self.db.flush()

        # Then merge the translations
        for benefit in self.link_benefit_constants:
            for translation in benefit.translations:
                translation.link_id = benefit.id
                self.db.merge(translation)

        self.db.commit()

    def _add_missing_aliases(self):

        benefit_translations = (
            self.db.query(LinkBenefitTranslationTable).filter(LinkBenefitTranslationTable.aliases.is_(None)).all()
        )

        for benefit_translation in benefit_translations:
            aliases = self.alias_generation_service.generate_alias(
                benefit_translation.title, benefit_translation.description
            )
            benefit_translation.aliases = aliases.aliases
            self.db.merge(benefit_translation)
            logger.info(f"Generated aliases for {benefit_translation.title}: {aliases}")

        self.db.commit()

    def _add_missing_translations(self):
        benefits = self.db.query(LinkBenefitTable).all()
        for benefit in benefits:
            translation = self.translation_service.create_missing_translations(benefit)
            self.db.add_all(translation)

        self.db.commit()

    def _add_missing_favicon_urls(self):
        link_favicon_urls = self.db.query(LinkBenefitTable).filter(LinkBenefitTable.favicon_url.is_(None)).all()
        for link in link_favicon_urls:
            link.favicon_url = self.favicon_service.get_favicon_url(link.url)
            self.db.merge(link)

        self.db.commit()
