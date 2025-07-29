from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
from typing import List
import json
from sqlalchemy.orm.session import Session
from typing_extensions import Optional
import datetime
import logging

from shared.src.tables.lectures import LectureTable
from data_fetcher.src.classes.models.lecture import Lecture, TreePath
from shared.src.enums.classes_enum import SemesterTypeEnum
from shared.src.tables.lectures.lecture_tables import *
from ..crawler.lsf_crawler import LSFCrawler
from shared.src.services.directus_service import DirectusService
from shared.src.core.logging import get_classes_logger

GRAPHQL_FOLDER_NAME = "graphql"
INSERT_LECTURE_QUERY_NAME = "insert_lecture.graphql"
UPDATE_LECTURE_QUERY_NAME = "update_lecture.graphql"
GET_LECTURE_QUERY_NAME = "get_lecture.graphql"


class LectureFetcher:
    """A class to fetch and store lectures from the LSF crawler into a Directus database."""

    def __init__(self) -> None:
        self.directus = DirectusService()
        self.lsf_crawler = LSFCrawler()
        self.workers: int = 5
        self.logger = get_classes_logger(__name__)


    def store_lectures_db(self, db: Session, year: int, semester: SemesterTypeEnum):
        """Store all lectures from the LSF crawler into the SQL database."""
        lectures = self.lsf_crawler.crawl_all_lectures_parallel(year, semester)

        for index, lecture in enumerate(lectures):
            if self.lecture_exist_in_db(db, lecture):
                self.update_lecture_db(db, lecture)
            else:
                self.add_lecture_db(db, lecture)
            self.logger.info(f"Processed Lecture {lecture.title}({index + 1}/{len(lectures)})")

    def update_lecture_db(self, session: Session, lecture: Lecture):
        """Update an existing lecture in the SQL database."""
        old = (
            session.query(LectureTable)
                .filter_by(publish_id=lecture.publish_id)
                .one_or_none()
        )
        if old:
            session.delete(old)
            session.flush()

        self.add_lecture_db(session, lecture)

    def add_lecture_db(self, session: Session, lecture: Lecture):
        """Add a lecture to the SQL database."""
        lecture_table, related = lecture.to_table()
        session.add(lecture_table)
        for key, entries in related.items():
            if key in {"persons", "institutions"}:
                for obj in entries:
                    session.merge(obj)
            else:
                session.add_all(entries)

        session.commit()


    def lecture_exist_in_db(self, session: Session, lecture: Lecture) -> bool:
        """Check if a lecture exists in the SQL database."""
        return bool(
            session.query(LectureTable)
            .filter_by(publish_id=lecture.publish_id)
            .one_or_none()
        )

    def store_lectures_if_not_exist_parallel(self, year: int, semester: SemesterTypeEnum) -> None:
        """
        Fetches all lectures for a given year and semester, checks if they exist in the database,
        and inserts them if they do not exist.
        This method uses parallel processing to speed up the insertion process.
        """
        lecture_list = self.lsf_crawler.crawl_all_lectures_parallel(year, semester)

        def process_lecture(lecture):
            for attempt in range(5):
                try:
                    if self.lecture_exists(lecture.publish_id):
                        return f"[SKIP] {lecture.title} ({lecture.publish_id}) already exists"

                    self.insert_lecture(lecture)
                    return f"[OK] {lecture.title} ({lecture.publish_id}) inserted"
                except Exception as e:
                    wait = 2**attempt
                    self.logger.info(
                        f"[RETRY {attempt+1}/5] {lecture.title} ({lecture.publish_id}) failed: {e} — retrying in {wait}s"
                    )
                    time.sleep(wait)
            return f"[FAIL] {lecture.title} ({lecture.publish_id}) failed permanently after 5 attempts"

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(process_lecture, lec) for lec in lecture_list]
            for index, future in enumerate(as_completed(futures)):
                self.logger.info(f"Processing lecture {index+1}/{len(futures)}")
                result = future.result()
                if result.startswith("[FAIL]"):
                    self.logger.error(result)
                else:
                    self.logger.info(result)

    def store_lectures_parallel(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all lectures for a given year and semester, checks if they exist in the database,
        and updates or inserts them as necessary.
        """
        lecture_list = self.lsf_crawler.crawl_all_lectures_parallel(year, semester)

        def process_lecture(lecture):
            for attempt in range(5):
                try:
                    if self.lecture_exists(lecture.publish_id):
                        self.update_lecture(lecture, lecture.publish_id)
                        return f"[UPDATED] {lecture.title} ({lecture.publish_id}) already exists"

                    self.insert_lecture(lecture)
                    return f"[INSERTED] {lecture.title} ({lecture.publish_id}) inserted"
                except Exception as e:
                    wait = 2**attempt
                    self.logger.info(
                        f"[RETRY {attempt+1}/5] {lecture.title} ({lecture.publish_id}) failed: {e} — retrying in {wait}s"
                    )
                    time.sleep(wait)
            return f"[FAIL] {lecture.title} ({lecture.publish_id}) failed permanently after 5 attempts"

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(process_lecture, lec) for lec in lecture_list]
            for index, future in enumerate(as_completed(futures)):
                self.logger.info(f"Processing lecture {index+1}/{len(futures)}")
                result = future.result()
                if result.startswith("[FAIL]"):
                    self.logger.error(f"Failed to process lecture {index+1}/{len(futures)}")
                else:
                    self.logger.info(f"Successfully processed lecture {index+1}/{len(futures)}")

    def store_lectures_if_not_exist(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all lectures for a given year and semester, checks if they exist in the database,
        and inserts them if they do not exist."""
        lecture_urls = self.lsf_crawler.crawl_all_lecture_urls_sequentially(year, semester)

        for index, (name, url) in enumerate(lecture_urls):
            self.logger.info(f"Processing lecture({len(lecture_urls)}/{index+1}): {name} ({url})")
            publish_id = LectureTable.publish_id_from_url(url)

            if self.lecture_exists(publish_id):
                continue

            lecture = self.lsf_crawler.build_complete_lecture_object(name, url)
            self.insert_lecture(lecture)
            self.logger.info(f"Succesfully processed lecture: {name} ({url})")

    def store_lectures(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all lectures for a given year and semester, checks if they exist in the database,
        and updates or inserts them as necessary."""
        lectures = self.lsf_crawler.crawl_all_lectures_parallel(year, semester)

        for index, lecture in enumerate(lectures):
            self.logger.info(f"Processing lecture ({index+1}/{len(lectures)}): {lecture.title} ({lecture.publish_id})")

            if id := self.lecture_exists(lecture.publish_id):
                self.update_lecture(lecture, id)
            else:
                self.insert_lecture(lecture)

            self.logger.info(f"Succesfully processed lecture: {lecture.title} ({lecture.publish_id})")

    def insert_lecture(self, lecture: Lecture) -> None:
        """Inserts a lecture into the database using a GraphQL query."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = INSERT_LECTURE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=lecture.to_dict(),
        )
        if response.get("errors"):
            self.logger.error(f"Error inserting lecture: {response['errors']}")

    def lecture_exists(self, publish_id: int) -> str | None:
        """Checks if a lecture with the given publish_id exists in the database."""
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = GET_LECTURE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"publish_id": publish_id},
        )
        lectures = response.get("data", {}).get("lecture", [])
        return lectures[0].get("id") if lectures else None

    def update_lecture(self, lecture: Lecture, id: str) -> None:
        """Updates an existing lecture in the database using a GraphQL query."""
        if not self.lecture_exists(lecture.publish_id):
            self.logger.error(f"No Lecture with publish_id {lecture.publish_id} exist.")

        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = UPDATE_LECTURE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"id": id} | lecture.to_dict(),
        )
        if response.get("errors"):
            self.logger.error(f"Error updating lecture: {response['errors']}")


def main():
    fetcher = LectureFetcher()
    date = datetime.datetime.now()
    fetcher.store_lectures(date.year, SemesterTypeEnum.SUMMER_SEMESTER)
    fetcher.store_lectures(date.year, SemesterTypeEnum.WINTER_SEMESTER)


if __name__ == "__main__":
    main()
