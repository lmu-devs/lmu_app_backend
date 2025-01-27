import asyncio

import schedule
from sqlalchemy.orm import Session

from data_fetcher.src.roomfinder.services.explore_service import RoomfinderService
from data_fetcher.src.state import running_explore
from shared.src.core.database import get_db
from shared.src.core.error_handlers import handle_error
from shared.src.core.logging import get_roomfinder_fetcher_logger


logger = get_roomfinder_fetcher_logger(__name__)

def fetch_scheduled_data(db: Session):
    service = RoomfinderService(db)
    service.update_database()
    
    logger.info("Successfully updated explore data")
    logger.info("================================================\n")

async def create_roomfinder_fetcher():
    logger.info("================================================")
    logger.info(f"Setting up {__name__}...")
    
    db = next(get_db())
    fetch_scheduled_data(db)
    
    while running_explore:
        schedule.run_pending()
        await asyncio.sleep(60)

    logger.info("================================================\n")