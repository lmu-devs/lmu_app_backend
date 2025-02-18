from sqlalchemy.orm import Session

from data_fetcher.src.links.constants.link_constants import link_constants
from shared.src.tables.links.links_table import LinkTable, LinkTranslationTable


class LinkService:
    def __init__(self, db: Session):
        self.db = db
        self.link_constants = link_constants
        
    def delete_links_not_in_constants(self):
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

    def merge_links_in_db(self):
        self.delete_links_not_in_constants()
        
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
