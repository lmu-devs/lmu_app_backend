from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
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

GRAPHQL_FOLDER_NAME = "graphql"
INSERT_COURSE_QUERY_NAME = "insert_lecture.graphql"
UPDATE_COURSE_QUERY_NAME = "update_lecture.graphql"
GET_COURSE_QUERY_NAME = "get_lecture.graphql"


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
        session.commit()

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

    def store_courses_db(self, db: Session, year: int, semester: SemesterTypeEnum):
        """Store all courses from the LSF crawler into the SQL database."""
        course_crawler = LSFParallelCrawler(year, semester)

        for index, course in enumerate(course_crawler):
            if self.course_exist_in_db(db, course):
                self.update_course_db(db, course)
            else:
                self.add_course_db(db, course)
            db.commit()
            self.logger.info(
                f"({index + 1}/{len(course_crawler)}) Processed Course {course.title}"
            )

    def update_course_db(self, session: Session, course: Course):
        """Update an existing course in the SQL database."""
        old = (
            session.query(CourseTable)
            .filter_by(publish_id=course.publish_id)
            .one_or_none()
        )
        if old:
            session.delete(old)
            session.flush()

        self.add_course_db(session, course)

    def course_exist_in_db(self, session: Session, course: Course) -> bool:
        """Check if a course exists in the SQL database."""
        return bool(
            session.query(CourseTable)
            .filter_by(publish_id=course.publish_id)
            .one_or_none()
        )

    def store_courses_if_not_exist_parallel(
        self, year: int, semester: SemesterTypeEnum
    ) -> None:
        """
        Fetches all courses for a given year and semester, checks if they exist in the database,
        and inserts them if they do not exist.
        This method uses parallel processing to speed up the insertion process.
        """
        course_list = self.lsf_crawler.crawl_all_courses_parallel(year, semester)

        def process_course(course: Course):
            for attempt in range(5):
                try:
                    if self.course_exists(course.publish_id):
                        return f"[SKIP] {course.title} ({course.publish_id}) already exists"

                    self.insert_course(course)
                    return f"[OK] {course.title} ({course.publish_id}) inserted"
                except Exception as e:
                    wait = 2**attempt
                    self.logger.info(
                        f"[RETRY {attempt + 1}/5] {course.title} ({course.publish_id}) failed: {e} — retrying in {wait}s"
                    )
                    time.sleep(wait)
            return f"[FAIL] {course.title} ({course.publish_id}) failed permanently after 5 attempts"

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(process_course, lec) for lec in course_list]
            for index, future in enumerate(as_completed(futures)):
                self.logger.info(f"Processing course {index + 1}/{len(futures)}")
                result = future.result()
                if result.startswith("[FAIL]"):
                    self.logger.error(result)
                else:
                    self.logger.info(result)

    def store_courses_parallel(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all courses for a given year and semester, checks if they exist in the database,
        and updates or inserts them as necessary.
        """
        course_list = self.lsf_crawler.crawl_all_courses_parallel(year, semester)

        def process_course(course: Course):
            for attempt in range(5):
                try:
                    if self.course_exists(course.publish_id):
                        self.update_course(course, str(course.publish_id))
                        return f"[UPDATED] {course.title} ({course.publish_id}) already exists"

                    self.insert_course(course)
                    return f"[INSERTED] {course.title} ({course.publish_id}) inserted"
                except Exception as e:
                    wait = 2**attempt
                    self.logger.info(
                        f"[RETRY {attempt + 1}/5] {course.title} ({course.publish_id}) failed: {e} — retrying in {wait}s"
                    )
                    time.sleep(wait)
            return f"[FAIL] {course.title} ({course.publish_id}) failed permanently after 5 attempts"

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(process_course, lec) for lec in course_list]
            for index, future in enumerate(as_completed(futures)):
                self.logger.info(f"Processing course {index + 1}/{len(futures)}")
                result = future.result()
                if result.startswith("[FAIL]"):
                    self.logger.error(
                        f"Failed to process course {index + 1}/{len(futures)}"
                    )
                else:
                    self.logger.info(
                        f"Successfully processed course {index + 1}/{len(futures)}"
                    )

    def store_courses_if_not_exist(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all courses for a given year and semester, checks if they exist in the database,
        and inserts them if they do not exist."""
        course_urls = self.lsf_crawler.crawl_all_course_urls_sequentially(
            year, semester
        )

        for index, (name, url) in enumerate(course_urls):
            self.logger.info(
                f"Processing course({len(course_urls)}/{index + 1}): {name} ({url})"
            )
            publish_id = CourseTable.publish_id_from_url(url)

            if self.course_exists(publish_id):
                continue

            course = self.lsf_crawler.build_complete_course_object(name, url)
            self.insert_course(course)
            self.logger.info(f"Succesfully processed course: {name} ({url})")

    def store_courses(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all courses for a given year and semester, checks if they exist in the database,
        and updates or inserts them as necessary."""
        courses = self.lsf_crawler.crawl_all_courses_parallel(year, semester)

        for index, course in enumerate(courses):
            self.logger.info(
                f"Processing course ({index + 1}/{len(courses)}): {course.title} ({course.publish_id})"
            )

            if id := self.course_exists(course.publish_id):
                self.update_course(course, id)
            else:
                self.insert_course(course)

            self.logger.info(
                f"Succesfully processed course: {course.title} ({course.publish_id})"
            )

    def insert_course(self, course: Course) -> None:
        """Inserts a course into the database using a GraphQL query."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = INSERT_COURSE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=course.to_dict(),
        )
        if response.get("errors"):
            self.logger.error(f"Error inserting course: {response['errors']}")

    def course_exists(self, publish_id: int) -> str | None:
        """Checks if a course with the given publish_id exists in the database."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = GET_COURSE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"publish_id": publish_id},
        )
        courses = response.get("data", {}).get("lecture", [])
        return courses[0].get("id") if courses else None

    def update_course(self, course: Course, id: str) -> None:
        """Updates an existing course in the database using a GraphQL query."""
        if not self.course_exists(course.publish_id):
            self.logger.error(f"No Course with publish_id {course.publish_id} exist.")

        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = UPDATE_COURSE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"id": id} | course.to_dict(),
        )
        if response.get("errors"):
            self.logger.error(f"Error updating course: {response['errors']}")


def main():
    fetcher = CourseFetcher()
    date = datetime.datetime.now()
    fetcher.store_courses(date.year, SemesterTypeEnum.SUMMER_SEMESTER)
    fetcher.store_courses(date.year, SemesterTypeEnum.WINTER_SEMESTER)


if __name__ == "__main__":
    main()
