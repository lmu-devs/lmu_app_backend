import asyncio
from abc import ABC, abstractmethod
from typing import Optional

import schedule

from shared.src.core.database import get_db
from shared.src.core.logging import get_main_fetcher_logger


class BaseCollector(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        self.logger = get_main_fetcher_logger(self.name)
        self.is_running = True

    def log_boundary(self, message: str):
        """Log a message with boundary markers"""
        self.logger.info("\n")
        self.logger.info("=" * 40)
        self.logger.info(message)

    @abstractmethod
    async def _collect_data(self, db):
        """Implement the actual data fetching logic"""
        raise NotImplementedError("Subclasses must implement _collect_data")

    async def collect(self):
        """Public method to collect data with database handling"""
        db = next(get_db())
        try:
            await self._collect_data(db)
            self.logger.info(f"✅ Collected data {self.name}")
        finally:
            db.close()

    async def run(self):
        """Main run loop for the collector - runs once"""
        self.log_boundary(f"🔄 Starting {self.name}")
        try:
            await self.collect()
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {e}", exc_info=True)
        finally:
            self.logger.info(f"⏹️  Shutting down {self.name}")
            self.logger.info("=" * 40)


class ScheduledCollector(BaseCollector):
    def __init__(self, job_schedule: Optional[schedule.Job] = None):
        """
        Initialize a scheduled collector
        Args:
            job_schedule: A schedule.Job instance defining when to run
        """
        super().__init__()
        self.job = job_schedule
        if job_schedule:
            # Wrap the collect coroutine in a sync function that runs it in the event loop
            def run_collect():
                asyncio.create_task(self.collect())

            job_schedule.do(run_collect)

    async def run(self):
        """Main run loop for scheduled collector - runs at scheduled times"""
        self.log_boundary(f"🔄 Starting {self.name}")
        self.logger.info("📅  Schedule Configuration:")
        self.logger.info(f"   • Interval: {self.job.interval}")
        self.logger.info(f"   • Next Run: {self.job.next_run.strftime('%H:%M:%S %d-%m-%Y')}")

        try:
            # Run immediately on startup
            await self.collect()

            # Then follow the schedule
            while self.is_running:
                next_run = schedule.idle_seconds()
                if next_run is None:
                    break

                await asyncio.sleep(next_run)
                schedule.run_pending()

        except Exception as e:
            self.logger.error(f"Error in {self.name}: {e}", exc_info=True)
        finally:
            self.logger.info(f"⏹️  Shutting down {self.name}")
            self.logger.info("=" * 40)
