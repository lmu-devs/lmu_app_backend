import asyncio
from abc import ABC, abstractmethod
from typing import Optional

import schedule

from shared.src.core.database import get_db
from shared.src.core.logging import get_main_fetcher_logger


class BaseCollector(ABC):
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self.logger = get_main_fetcher_logger(f"fetcher.{self.name}")
        self.is_running = True
    
    def log_boundary(self, message: str):
        """Log a message with boundary markers"""
        self.logger.info("=" * 50)
        self.logger.info(message)
        self.logger.info("=" * 50)
    
    @abstractmethod
    async def _collect_data(self, db):
        """Implement the actual data fetching logic"""
        raise NotImplementedError("Subclasses must implement _collect_data")

    async def collect(self):
        """Public method to collect data with database handling"""
        db = next(get_db())
        try:
            await self._collect_data(db)
            self.logger.info(f"✅ collected data for {self.name}")
        finally:
            db.close()

    async def run(self):
        """Main run loop for the fetcher"""
        self.log_boundary(f"Starting {self.name}")
        
        try:
            while self.is_running:
                await self.collect()
                schedule.run_pending()
                await asyncio.sleep(60)
        except Exception as e:
            self.logger.error(f"Error in {self.name} fetcher: {e}", exc_info=True)
        finally:
            self.log_boundary(f"Shutting down {self.name} fetcher")

class ScheduledCollector(BaseCollector):
    def __init__(self, job_schedule: Optional[schedule.Job] = None):
        """
        Initialize a scheduled fetcher
        Args:
            job_schedule: A schedule.Job instance defining when to run
        """
        super().__init__()
        if job_schedule:
            job_schedule.do(self.collect) 