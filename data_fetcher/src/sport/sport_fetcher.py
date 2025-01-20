import asyncio

from shared.src.core.database import get_db
from shared.src.core.logging import get_main_fetcher_logger

from ..state import running_sport


logger = get_main_fetcher_logger(__name__)

async def create_university_fetcher():
    logger.info("================================================")
    logger.info(f"Setting up {__name__}...")
    
    db = next(get_db())
    # add_university_to_database(db)
    
    
    while running_sport:
        await asyncio.sleep(3600*24)

    logger.info(f"Exiting {__name__} loop...")
    logger.info("================================================\n")