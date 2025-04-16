import json
import logging
from typing import Dict, List

import requests

from ..models.course_model import Course

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LMUCourseScraper:
    def __init__(self):
        self.base_url = "https://cms-search.lmu.de/search/courses_by_name_asc/execute"
        self.headers = {
            "Accept": "application/json",
            "Origin": "https://www.lmu.de",
            "Referer": "https://www.lmu.de/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Authorization": "Basic aGF1cGlhX3NlYXJjaF9wcm94eUBsbXUuZGU6aGF1cGlhX3NlYXJjaF9wcm94eQ==",
        }

    def fetch_courses(self, page: int = 1, num_rows: int = None) -> List[Course]:
        """
        Fetch courses from the LMU API

        Args:
            page (int): Page number to fetch
            num_rows (int): Number of results per page. If None, will first fetch to determine total.

        Returns:
            List[Course]: List of course objects
        """
        # First fetch to get total number of rows if num_rows not specified
        if num_rows is None:
            initial_params = {
                "query": "*",
                "language": ["de", "en"],
                "page": 1,
                "numRows": 1,
            }

            try:
                response = requests.get(self.base_url, params=initial_params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                num_rows = data.get("numRows", 50)  # Default to 50 if can't get total
                logger.info(f"Total number of courses found: {num_rows}")
            except requests.RequestException as e:
                logger.error(f"Error fetching total rows: {e}")
                num_rows = 50  # Default to 50 if request fails

        params = {
            "query": "*",
            "language": ["de", "en"],
            "page": page,
            "numRows": num_rows,
        }

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            courses_data = data.get("results", [])

            # Convert to Course objects
            courses = [Course(**course_data) for course_data in courses_data]

            # Log the first course for validation
            if courses:
                logger.info("First course data (for validation):")
                logger.info(json.dumps(courses[0].dict(), indent=2, ensure_ascii=False))

            return courses

        except requests.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            return []

    def extract_course_info(self, course: Dict) -> Dict:
        """
        Extract relevant information from a course dictionary

        Args:
            course (Dict): Course data dictionary

        Returns:
            Dict: Extracted course information
        """
        return {
            "name": course.get("Name_value", [None])[0],
            "degree": course.get("Degree_of_completion_value", [None])[0],
            "language": course.get("Language_value", [None])[0],
            "description": course.get("Description_value", [None])[0],
            "description_long": course.get("Description_long_value", [None])[0],
            # "ects": course.get("ECTS_value", [None])[0],
            # "type": course.get("Type_value", [None])[0],
            # "start_of_studies": course.get("Start_of_studies_value", [None])[0],
            # "teaching_language": course.get("teachingLanguage_value", [None])[0],
            "standard_period": course.get("standardPeriodOfStudy_value", [None])[0],
        }


def main():
    scraper = LMUCourseScraper()
    courses = scraper.fetch_courses()  # Will automatically fetch total number of rows

    if courses:
        logger.info(f"\nSuccessfully fetched {len(courses)} courses")

        # Save to JSON file
        with open("data_fetcher/src/course/temp/lmu_courses.json", "w", encoding="utf-8") as f:
            # Convert Course objects to dictionaries
            courses_data = [course.dict() for course in courses]
            json.dump(courses_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved courses to lmu_courses.json")


if __name__ == "__main__":
    main()
