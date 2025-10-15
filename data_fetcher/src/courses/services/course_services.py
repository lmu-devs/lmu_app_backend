from typing import List
from sqlalchemy.orm.session import Session
from typing_extensions import Optional
import datetime

from data_fetcher.src.courses.models.course import Course
from shared.src.enums.courses_enums import SemesterTypeEnum
from shared.src.tables.courses.course_tables import CourseTable
from ..crawler.lsf_crawler import LSFCrawler, LSFParallelCrawler
from shared.src.services.directus_service import DirectusService
from shared.src.core.logging import get_course_logger


class CourseFetcher:
    """A class to fetch and store courses from the LSF crawler into a Directus database."""

    def __init__(self) -> None:
        self.directus = DirectusService()
        self.lsf_crawler = LSFCrawler()
        self.workers: int = 5
        self.logger = get_course_logger(__name__)

    def store_courses_streaming_upsert(
        self, db: Session, year: int, semester: SemesterTypeEnum
    ):
        """Store courses using streaming + upsert for maximum efficiency."""
        courses_crawler = LSFParallelCrawler(year, semester)
        batch_courses: list[Course] = []
        batch_size = 100
        ids = {id_tuple[0] for id_tuple in db.query(CourseTable.publish_id).all()}

        for index, course in enumerate(courses_crawler):
            self.logger.info(
                f"Collecting Batch ({(index + 1) % batch_size}/{batch_size})"
                + f" from ({index + 1}/{len(courses_crawler)}) courses"
            )

            batch_courses.append(course)
            if len(batch_courses) >= batch_size:
                self._insert_course_batch(db, batch_courses, ids)
                db.commit()
                batch_courses = []

        if batch_courses:
            self._insert_course_batch(db, batch_courses, ids)
            db.commit()

    def _insert_course_batch(
        self, db: Session, batch: List[Course], publish_ids: set[int]
    ):
        for index, course in enumerate(batch):
            if course.publish_id in publish_ids:
                self.delete_old_course_db(db, course.publish_id)
            self.add_course_db(db, course)
            self.logger.info(
                f"Added Course in Batch ({index + 1}/{len(batch)}): {course.title}"
            )

    def delete_old_course_db(self, session: Session, course_id: int):
        course = session.get(CourseTable, course_id)

        if not course:
            return

        for institution in list(course.institutions):
            course.institutions.remove(institution)
            session.delete(institution)

        for person in list(course.persons):
            course.persons.remove(person)
            session.delete(person)

        session.delete(course)

    def add_course_db(self, session: Session, course: Course):
        """Add a course to the SQL database."""
        course_table, related = course.to_table()
        session.add(course_table)
        for key, entries in related.items():
            if key == "persons":
                for obj in entries:
                    merged = session.merge(obj)
                    course_table.persons.append(merged)
            elif key == "institutions":
                for obj in entries:
                    merged = session.merge(obj)
                    course_table.institutions.append(merged)
            else:
                session.add_all(entries)
