from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
from typing import List
import json
import tqdm

from data_fetcher.src.classes.models.lecture import Lecture
from shared.src.enums.classes_enum import SemesterTypeEnum
from ..crawler.lsf_crawler import LSFCrawler
from shared.src.services.directus_service import DirectusService

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
                    tqdm.tqdm.write(
                        f"[RETRY {attempt+1}/5] {lecture.title} ({lecture.publish_id}) failed: {e} — retrying in {wait}s"
                    )
                    time.sleep(wait)
            return f"[FAIL] {lecture.title} ({lecture.publish_id}) failed permanently after 5 attempts"

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(process_lecture, lec) for lec in lecture_list]
            for future in tqdm.tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Inserting lectures",
            ):
                result = future.result()
                tqdm.tqdm.write(result)

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
                    tqdm.tqdm.write(
                        f"[RETRY {attempt+1}/5] {lecture.title} ({lecture.publish_id}) failed: {e} — retrying in {wait}s"
                    )
                    time.sleep(wait)
            return f"[FAIL] {lecture.title} ({lecture.publish_id}) failed permanently after 5 attempts"

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(process_lecture, lec) for lec in lecture_list]
            for future in tqdm.tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Inserting lectures",
            ):
                result = future.result()
                tqdm.tqdm.write(result)

    def store_lectures_if_not_exist(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all lectures for a given year and semester, checks if they exist in the database,
        and inserts them if they do not exist."""
        self.lsf_crawler.year = year
        self.lsf_crawler.semester_type = semester
        lecture_urls = self.lsf_crawler._crawl_all_lecture_urls_sequentially()
        for name, url in tqdm.tqdm(lecture_urls, desc="Crawling and Storing lectures"):
            tqdm.tqdm.write(f"Processing lecture: {name} ({url})")
            publish_id = Lecture.publish_id_from_url(url)
            if self.lecture_exists(publish_id):
                continue
            lecture = self.lsf_crawler._build_complete_lecture_object((name, url))
            self.insert_lecture(lecture)
            tqdm.tqdm.write(f"Succesfully processed lecture: {name} ({url})")

    def store_lectures(self, year: int, semester: SemesterTypeEnum) -> None:
        """Fetches all lectures for a given year and semester, checks if they exist in the database,
        and updates or inserts them as necessary."""
        self.lsf_crawler.year = year
        self.lsf_crawler.semester_type = semester
        lecture_urls = self.lsf_crawler._crawl_all_lecture_urls_sequentially()
        for name, url in tqdm.tqdm(lecture_urls, desc="Crawling and Storing lectures"):
            tqdm.tqdm.write(f"Processing lecture: {name} ({url})")
            lecture = self.lsf_crawler._build_complete_lecture_object((name, url))
            if id := self.lecture_exists(lecture.publish_id):
                self.update_lecture(lecture, id)
            else:
                self.insert_lecture(lecture)
            tqdm.tqdm.write(f"Succesfully processed lecture: {name} ({url})")

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
            raise Exception(f"Error inserting lecture: {response['errors']}")

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
            raise Exception(f"No Lecture with publish_id {lecture.publish_id} exist.")

        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = UPDATE_LECTURE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables={"id": id} | lecture.to_dict(),
        )
        if response.get("errors"):
            raise Exception(f"Error updating lecture: {response['errors']}")


def main():
    fetcher = LectureFetcher()
    fetcher.store_lectures_if_not_exist_parallel(2025, SemesterTypeEnum.SUMMER_SEMESTER)


if __name__ == "__main__":
    main()
