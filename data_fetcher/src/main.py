import asyncio
import signal
import sys

from data_fetcher.src.cinema.cinema_fetcher import create_cinema_fetcher
from data_fetcher.src.food.food_fetcher import create_food_fetcher
from data_fetcher.src.roomfinder.explore_fetcher import create_roomfinder_fetcher
from data_fetcher.src.sport.sport_fetcher import create_sport_fetcher
from data_fetcher.src.university.university_fetcher import create_university_fetcher
from shared.src.core.database import Base, Database, get_async_db, table_creation
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.core.settings import get_settings


logger_main = get_main_fetcher_logger(__name__)

# # ------ Needed for stopping docker container ------ #
# def signal_handler(signum, frame):
#     global running_eat
#     global running_movie
#     logger_main.info("Received shutdown signal. Stopping gracefully...")

# # Register the signal handler
# signal.signal(signal.SIGTERM, signal_handler)
# signal.signal(signal.SIGINT, signal_handler)
# # ------ Needed for stopping docker container ------ #

async def main():
    logger_main.info("================================================")
    logger_main.info("data_fetcher started")
    try:
        settings = get_settings()
        Database(settings=settings)
        table_creation()
        async_db = get_async_db()
        
        tasks = [
            # asyncio.create_task(create_university_fetcher()),
            # asyncio.create_task(create_cinema_fetcher()),
            # asyncio.create_task(create_food_fetcher()),
            # asyncio.create_task(create_sport_fetcher()),
            asyncio.create_task(create_roomfinder_fetcher())
        ]
        
        await asyncio.gather(*tasks)
        
    except Exception as e:
        logger_main.error(f"An error occurred: {e}")
    finally:
        logger_main.info("data_fetcher is shutting down")
        logger_main.info("================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
