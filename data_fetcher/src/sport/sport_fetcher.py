import asyncio
import schedule

from shared.src.core.database import get_db
from shared.src.core.logging import get_main_fetcher_logger

from ..state import running_sport
from .services.sport_service import add_sport_to_database


logger = get_main_fetcher_logger(__name__)

async def create_sport_fetcher():
    logger.info("================================================")
    logger.info(f"Setting up {__name__}...")
    
    db = next(get_db())
    add_sport_to_database(db)
    
    async def scheduled_task():
        add_sport_to_database(db)
        
    schedule.every().hour.at(":55").do(scheduled_task)
    
    while running_sport:
        schedule.run_pending()
        await asyncio.sleep(60)

    logger.info(f"Exiting {__name__} loop...")
    logger.info("================================================\n")