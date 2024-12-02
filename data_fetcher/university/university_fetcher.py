from data_fetcher.university.services.university_service import add_university_to_database
from shared.database import get_db
from shared.core.logging import get_main_fetcher_logger

logger = get_main_fetcher_logger(__name__)

def create_university_fetcher():
    logger.info("Starting university fetcher")
    
    db = next(get_db())
    
    # Initial fetch
    add_university_to_database(db)
    
    logger.info("Finished adding universities to database")


