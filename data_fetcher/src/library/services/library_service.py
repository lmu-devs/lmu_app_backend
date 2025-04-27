from typing import List

from sqlalchemy.orm import Session

from data_fetcher.src.library.crawler.library_crawler import LibraryCrawler
from data_fetcher.src.library.models.library_model import Library
from shared.src.core.logging import get_library_logger

logger = get_library_logger(__name__)


class LibraryService:
    def __init__(self, db: Session):
        self.db = db
        self.crawler = LibraryCrawler()

    def update_library_data(self, library: Library):
        pass

    def get_library_data(self):
        libraries = self.crawler._parse_libraries_list()
        libraries_data: List[Library] = []
        total = len(libraries)
        for i, library in enumerate(libraries):
            logger.info(f"[{i + 1}/{total}] Processing library")
            result = self.crawler.get_library(library)
            if result:
                self.update_library_data(result)

        if libraries_data:
            logger.info(f"Successfully crawled {len(libraries_data)} library entries.")
        else:
            logger.error("Crawling returned no library data. File not saved.")

        logger.info("Munich Library Crawler script finished.")
