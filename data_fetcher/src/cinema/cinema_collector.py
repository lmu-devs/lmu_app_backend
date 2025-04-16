import schedule

from data_fetcher.src.cinema.services.cinema_service import CinemaService
from data_fetcher.src.core.base_collector import ScheduledCollector
from shared.src.core.logging import get_cinema_fetcher_logger


class CinemaCollector(ScheduledCollector):
    def __init__(self):
        job_schedule = schedule.every().monday.at("08:08")
        super().__init__(job_schedule=job_schedule)
        self.logger = get_cinema_fetcher_logger(__name__)

    async def _collect_data(self, db):
        service = CinemaService(db)

        service.add_constant_cinema_data()
        await service.fetch_scheduled_data()
