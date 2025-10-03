from data_fetcher.src.core.base_collector import ScheduledCollector
from data_fetcher.src.courses.services.course_services import CourseFetcher
from shared.src.enums.courses_enums import SemesterTypeEnum
from shared.src.core.logging import get_course_logger

import schedule
import datetime


class CoursesCollector(ScheduledCollector):
    """A collector to fetch and store courses from the LSF crawler into a Directus database."""

    def __init__(self):
        super().__init__(job_schedule=schedule.every().monday.at("00:00"))
        self.logger = get_course_logger(__name__)
        self.course_fetcher = CourseFetcher()

    async def _collect_data(self, db):
        date = datetime.datetime.now()
        self.logger.info(f"Collecting summer and winter semester for {date.year}")

        self.course_fetcher.store_courses_streaming_upsert(
            db, date.year, SemesterTypeEnum.SUMMER_SEMESTER
        )
        self.logger.info(f"Summer semester collected in {date.year}")

        self.course_fetcher.store_courses_streaming_upsert(
            db, date.year, SemesterTypeEnum.WINTER_SEMESTER
        )
        self.logger.info(f"Winter semester collected in {date.year}")


if __name__ == "__main__":
    collector = CoursesCollector()
