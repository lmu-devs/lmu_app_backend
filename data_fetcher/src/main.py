import asyncio
import signal
import sys

from shared.src.core.database import Database
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.core.settings import get_settings

from data_fetcher.src.university.university_fetcher import create_university_fetcher
from data_fetcher.src.cinema.cinema_fetcher import create_movie_fetcher

logger_main = get_main_fetcher_logger(__name__)

# ------ Needed for stopping docker container ------ #
def signal_handler(signum, frame):
    global running_eat
    global running_movie
    logger_main.info("Received shutdown signal. Stopping gracefully...")

# Register the signal handler
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
# ------ Needed for stopping docker container ------ #

async def main():
    logger_main.info("================================================")
    logger_main.info("data_fetcher started")
    try:
        settings = get_settings()
        Database(settings=settings)
        
        tasks = [
            asyncio.create_task(create_university_fetcher()),
            # asyncio.create_task(create_movie_fetcher()),
            # asyncio.create_task(create_food_fetcher())
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
