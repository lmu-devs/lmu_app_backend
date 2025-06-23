from data_fetcher.src.core.base_collector import ScheduledCollector
from services.lecture_service import LectureFetcher
from shared.src.enums.classes_enum import SemesterTypeEnum


class ClassesCollecter(ScheduledCollector):
    """A collector to fetch and store lectures from the LSF crawler into a Directus database."""

    def __init__(self):
        # super().__init__(job_schedule=schedule.every().day.at("09:00"))
        self.lecture_fetcher = LectureFetcher()

    async def _collect_data(self, db):
        self.lecture_fetcher.store_lectures(2025, SemesterTypeEnum.SUMMER_SEMESTER)
