import schedule

from data_fetcher.src.core.base_collector import ScheduledCollector
from data_fetcher.src.library.services.library_service import LibraryService


class LibraryCollector(ScheduledCollector):
    def __init__(self):
        super().__init__(job_schedule=schedule.every().day.at("02:00"))

    async def _collect_data(self, db):
        service = LibraryService(db)
        service.run()
