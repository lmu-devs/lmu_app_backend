import asyncio
import signal
import sys

from data_fetcher.src.cinema.cinema_collector import CinemaCollector
from data_fetcher.src.food.food_collector import FoodCollector
from data_fetcher.src.library.library_collector import LibraryCollector
from data_fetcher.src.link.link_collector import LinkCollector
from data_fetcher.src.roomfinder.explore_collector import RoomfinderCollector
from data_fetcher.src.sport.sport_collector import SportCollector
from data_fetcher.src.university.university_collector import UniversityCollector
from shared.src.core.database import Database, table_creation
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.core.settings import get_settings

logger = get_main_fetcher_logger(__name__)


class DataCollectorApp:
    def __init__(self):
        self.settings = get_settings()
        self.is_running = True
        self.collectors = [
            LinkCollector(),
            UniversityCollector(),
            RoomfinderCollector(),
            LibraryCollector(),
            # FoodCollector(),
            SportCollector(),
            CinemaCollector(),
        ]

    async def setup(self):
        """Initialize database and other resources"""
        Database(settings=self.settings)
        table_creation()

    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""

        def signal_handler(signum, frame):
            logger.info("Received shutdown signal. Stopping gracefully...")
            self.is_running = False

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    async def run(self):
        """Main application runner"""
        logger.info("=" * 50)
        logger.info("Data Fetcher Starting")

        try:
            await self.setup()

            tasks = [asyncio.create_task(collector.run()) for collector in self.collectors]

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
        finally:
            logger.info("Data Fetcher Shutting Down")
            logger.info("=" * 40)


async def main():
    app = DataCollectorApp()
    app.setup_signal_handlers()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
