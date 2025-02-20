from sqlalchemy.orm import Session

from data_fetcher.src.core.services.alias_generation_service import AliasGenerationService
from data_fetcher.src.core.services.favicon_service import FaviconService
from data_fetcher.src.links.constants.link_constants import link_constants
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.translation_service import TranslationService
from shared.src.tables.links.links_table import LinkTable, LinkTranslationTable

from shared.src.core.logging import get_translation_logger

logger = get_translation_logger(__name__)


class LinkService:
    def __init__(self, db: Session):
        self.db = db
        self.link_constants = link_constants
        self.translation_service = TranslationService()
        self.alias_generation_service = AliasGenerationService()
        self.favicon_service = FaviconService()
        
    def run(self):
        self._merge_links_in_db()
        self._add_missing_aliases()
        self._add_missing_translations()
        self._add_missing_favicon_urls()
        
    def _delete_links_not_in_constants(self):
        # Get the set of link IDs from constants
        constant_link_ids = {link.id for link in self.link_constants}
        
        # First delete translations for links that aren't in constants
        self.db.query(LinkTranslationTable).filter(
            ~LinkTranslationTable.link_id.in_(constant_link_ids)
        ).delete(synchronize_session=False)
        
        # Then delete the links that aren't in constants
        self.db.query(LinkTable).filter(
            ~LinkTable.id.in_(constant_link_ids)
        ).delete(synchronize_session=False)

    def _merge_links_in_db(self):
        self._delete_links_not_in_constants()
        
        # Merge the links from constants
        for link in self.link_constants:
            base_link = LinkTable(
                id=link.id,
                url=link.url,
                favicon_url=link.favicon_url,
                types=link.types
            )
            self.db.merge(base_link)
            
        self.db.flush()
        
        # Then merge the translations
        for link in self.link_constants:
            for translation in link.translations:
                translation.link_id = link.id
                self.db.merge(translation)
                
        self.db.commit()
        
        
        
    def _add_missing_aliases(self):
        
        link_translations = self.db.query(LinkTranslationTable).filter(LinkTranslationTable.aliases.is_(None)).all()
        
        for link_translation in link_translations:
            aliases = self.alias_generation_service.generate_alias(link_translation.title, link_translation.description)
            link_translation.aliases = aliases.aliases
            self.db.merge(link_translation)
            logger.info(f"Generated aliases for {link_translation.title}: {aliases}")
            
        self.db.commit()
        
        
    def _add_missing_translations(self):
        links = self.db.query(LinkTable).all()
        for link in links:
            translation = self.translation_service.create_missing_translations(link)
            self.db.add_all(translation)
        
        self.db.commit()
        
    def _add_missing_favicon_urls(self):
        
        link_favicon_urls = self.db.query(LinkTable).filter(LinkTable.favicon_url.is_(None)).all()
        for link in link_favicon_urls:
            link.favicon_url = self.favicon_service.get_favicon_url(link.url)
            self.db.merge(link)
        
        self.db.commit()

        
        
                
