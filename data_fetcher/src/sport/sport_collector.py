import schedule

from data_fetcher.src.core.base_collector import ScheduledCollector
from data_fetcher.src.sport.services.sport_service import SportService


class SportCollector(ScheduledCollector):
    def __init__(self):
        super().__init__(job_schedule=schedule.every().day.at("02:13"))

    async def _collect_data(self, db):
        service = SportService(db)
        service.update_sport_courses()
