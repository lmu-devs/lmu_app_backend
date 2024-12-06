import asyncio
from data_fetcher.university.services.university_service import add_university_to_database
from shared.database import get_db
from shared.core.logging import get_main_fetcher_logger

from data_fetcher.state import running_university

logger = get_main_fetcher_logger(__name__)

async def create_university_fetcher():
    logger.info("================================================")
    logger.info(f"Setting up {__name__}...")
    
    db = next(get_db())
    add_university_to_database(db)
    
    
    while running_university:
        await asyncio.sleep(3600*24)

    logger.info(f"Exiting {__name__} loop...")
    logger.info("================================================\n")

