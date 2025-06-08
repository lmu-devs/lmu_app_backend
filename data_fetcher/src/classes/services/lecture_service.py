from typing import List
from data_fetcher.src.classes.models.lecture import Lecture
from shared.src.enums.classes_enum import SemesterTypeEnum
from ..crawler.lsf_crawler import LSFCrawler


class LectureFetcher:
    def __init__(self) -> None:
        self.lsf_crawler = LSFCrawler()

    def store_lectures(self, year: int, semester: SemesterTypeEnum) -> None:
        lectures = self.lsf_crawler.crawl_all_lectures(year, semester)

        for lecture in lectures:
            variables = self.build_lecture_variables(lecture)

    def build_lecture_variables(self, lecture: Lecture) -> dict:
        return [
            {
                "publish_id": lecture.publish_id,
                "title": lecture.title,
                "tree_path": [path.path for path in lecture.tree_paths],
            }
        ]
