from data_fetcher.src.core.base_collector import ScheduledCollector
from services.lecture_service import LectureFetcher
from shared.src.enums.classes_enum import SemesterTypeEnum

import schedule
import datetime


class ClassesCollecter(ScheduledCollector):
    """A collector to fetch and store lectures from the LSF crawler into a Directus database."""

    def __init__(self):
        super().__init__(job_schedule=schedule.every().monday.at("00:00"))
        self.lecture_fetcher = LectureFetcher()

    async def _collect_data(self, db):
        date = datetime.datetime.now()
        self.lecture_fetcher.store_lectures(date.year, SemesterTypeEnum.SUMMER_SEMESTER)
        self.lecture_fetcher.store_lectures(date.year, SemesterTypeEnum.WINTER_SEMESTER)
