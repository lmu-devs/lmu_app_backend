from data_fetcher.src.core.base_collector import ScheduledCollector
from data_fetcher.src.classes.services.lecture_service import LectureFetcher
from shared.src.enums.classes_enum import SemesterTypeEnum
from shared.src.core.logging import get_classes_logger

import schedule
import datetime


class ClassesCollecter(ScheduledCollector):
    """A collector to fetch and store lectures from the LSF crawler into a Directus database."""

    def __init__(self):
        super().__init__(job_schedule=schedule.every().monday.at("00:00"))
        self.logger = get_classes_logger(__name__)
        self.lecture_fetcher = LectureFetcher()

    async def _collect_data(self, db):
        date = datetime.datetime.now()
        self.logger.info(f"Collecting summer and winter semester for {date.year}")

        self.lecture_fetcher.store_lectures_streaming_upsert(db, date.year, SemesterTypeEnum.SUMMER_SEMESTER)
        self.logger.info(f"Summer semester collected in {date.year}")

        self.lecture_fetcher.store_lectures_streaming_upsert(db, date.year, SemesterTypeEnum.WINTER_SEMESTER)
        self.logger.info(f"Winter semester collected in {date.year}")




if __name__ == "__main__":
    collector = ClassesCollecter()
