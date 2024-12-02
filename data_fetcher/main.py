import asyncio
import signal
import sys

from data_fetcher.eat.eat_fetcher import create_eat_fetcher
from data_fetcher.movie.movie_fetcher import create_movie_fetcher
from data_fetcher.university.university_fetcher import create_university_fetcher
from data_fetcher.state import running_eat, running_movie
from shared.core.logging import get_main_fetcher_logger
from shared.database import Database
from shared.settings import get_settings

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


if __name__ == "__main__":
    logger_main.info("data_fetcher started")
    try:
        # Initialize the database
        settings = get_settings()
        Database(settings=settings)
        
        # Start the main loop
        # create_university_fetcher()
        # create_eat_fetcher()
        asyncio.run(create_movie_fetcher())
        
    except Exception as e:
        logger_main.error(f"An error occurred: {e}")
    finally:
        logger_main.info("data_fetcher is shutting down")
    sys.exit(0)
