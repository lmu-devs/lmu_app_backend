from pathlib import Path
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
    def __init__(self) -> None:
        self.directus = DirectusService()
        self.lsf_crawler = LSFCrawler()

    def store_lectures(self, year: int, semester: SemesterTypeEnum) -> None:
        lectures = self.lsf_crawler.crawl_all_lectures(year, semester)
        for lecture in tqdm.tqdm(lectures, desc="Storing lectures"):
            if not (id := self.lecture_exists(lecture.publish_id)):
                self.insert_lecture(lecture)
            else:
                self.update_lecture(lecture, id)

    def build_lecture_variables(self, lecture: Lecture) -> dict:
        tree_paths = (
            [p.path for p in lecture.tree_paths] if lecture.tree_paths else None
        )
        return {
            "publish_id": lecture.publish_id,
            "title": lecture.title,
            "paths": json.dumps(tree_paths),
        }

    def build_update_lecture_variables(self, lecture: Lecture, id: str) -> dict:
        tree_paths = (
            [p.path for p in lecture.tree_paths] if lecture.tree_paths else None
        )
        return {
            "id": id,
            "title": lecture.title,
            "paths": json.dumps(tree_paths),
        }

    def insert_lecture(self, lecture: Lecture) -> None:
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = INSERT_LECTURE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=self.build_lecture_variables(lecture),
        )
        if response.get("errors"):
            raise Exception(f"Error inserting lecture: {response['errors']}")

    def lecture_exists(self, publish_id: int) -> str | None:
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
        if not self.lecture_exists(lecture.publish_id):
            raise Exception(f"No Lecture with publish_id {lecture.publish_id} exist.")

        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = UPDATE_LECTURE_QUERY_NAME
        query_path = base_path / folder / query_name

        response = self.directus.execute_query_file(
            query_file_path=query_path,
            variables=self.build_update_lecture_variables(lecture, id),
        )
        if response.get("errors"):
            raise Exception(f"Error updating lecture: {response['errors']}")


def main():
    fetcher = LectureFetcher()
    fetcher.store_lectures(2025, SemesterTypeEnum.SUMMER_SEMESTER)


if __name__ == "__main__":
    main()
