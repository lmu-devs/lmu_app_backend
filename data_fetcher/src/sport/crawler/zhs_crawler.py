import html
import json
from typing import Any, Dict, List

import requests

from data_fetcher.src.sport.models.sport_models import (
    Course,
    Price,
    SportCourse,
    SportCourseLocation,
    TimeFrame,
    TimeSlot,
)
from shared.src.core.logging import get_sport_fetcher_logger

logger = get_sport_fetcher_logger(__name__)


class ZhsCrawler:
    def __init__(self):
        self.base_url = "https://www.buchung.zhs-muenchen.de"
        self.search_url = f"{self.base_url}/angebote/aktueller_zeitraum_0/kurssuche.js"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _extract_js_data(self, js_content: str) -> Dict[str, Any]:
        """Extract data from JavaScript content"""
        try:
            # Find the data object in the JS content
            start = js_content.find("var data = ") + len("var data = ")
            if start == -1:
                logger.error("Could not find 'var data = ' in JS content")
                return {}

            # Clean up JavaScript to make it valid JSON
            data_str = js_content[start:]

            # First decode standard HTML entities
            data_str = html.unescape(data_str)

            # Find the end of the JSON object
            brace_count = 0
            end_pos = 0
            for i, char in enumerate(data_str):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break

            if end_pos == 0:
                logger.error("Could not find matching braces in JS content")
                return {}

            data_str = data_str[:end_pos]
            return json.loads(data_str)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JS data: {str(e)}")
            logger.error(f"Error position: char {e.pos}")
            logger.error(f"Context: {js_content[e.pos-50:e.pos+50]}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error parsing JS data: {str(e)}")
            return {}

    def get_courses(self, exclude_keywords: List[str] = None) -> List[SportCourse]:
        """
        Fetch all courses from the ZHS website and group them by title

        Args:
            exclude_keywords: List of keywords to filter out courses (case-insensitive)

        Returns:
            List of SportCourse objects
        """
        try:
            response = requests.get(self.search_url, headers=self.headers)
            response.raise_for_status()

            # Extract data from JavaScript
            data = self._extract_js_data(response.text)
            if not data or "kurse" not in data or "tage" not in data:
                logger.error("Could not find course data or tage data in JS file")
                return []

            # First collect all courses
            course_dict: Dict[str, List[Course]] = {}

            for course_data in data["kurse"]:
                # Skip if course_data doesn't have enough elements
                if len(course_data) < 13:
                    continue

                # Skip if course is not available
                if course_data[0] < 0:
                    continue

                # Extract course info
                course_id = course_data[1]
                title = course_data[2]  # This is the sport type/title

                def _transform_name(name: str) -> str:
                    # Direct matches
                    if name == "A":
                        return "Anfänger (A)"
                    if name == "F":
                        return "Fortgeschritten (F)"
                    if name == "L":
                        return "Leistungssport (L)"

                    # Handle combinations with slash
                    name = name.replace("F/L", "Fortgeschritten / Leistungssport (F/L)")
                    name = name.replace("A/F", "Anfänger / Fortgeschritten (A/F)")

                    # Handle cases where it's a single letter with comma or space
                    name = name.replace("F,", "Fortgeschritten (F),")
                    name = name.replace("F ", "Fortgeschritten (F) ")
                    name = name.replace("A,", "Anfänger (A),")
                    name = name.replace("A ", "Anfänger (A) ")
                    name = name.replace("L,", "Leistungssport (L),")
                    name = name.replace("L ", "Leistungssport (L) ")

                    # Handle cases where letter is at the end
                    if name.endswith(" A"):
                        name = name[:-2] + " Anfänger (A)"
                    if name.endswith(" F"):
                        name = name[:-2] + " Fortgeschritten (F)"
                    if name.endswith(" L"):
                        name = name[:-2] + " Leistungssport (L)"

                    return name

                name = _transform_name(course_data[3])  # This is the specific course name/level

                # Skip if title contains any excluded keywords
                if exclude_keywords and any(keyword.lower() in title.lower() for keyword in exclude_keywords):
                    continue

                try:
                    course = Course(
                        id=course_id,
                        name=name,
                        time_slots=TimeSlot.from_pattern(course_data[4], course_data[5], data["tage"]),
                        duration=TimeFrame.from_duration_string(course_data[7]),
                        instructor=course_data[8],
                        price=Price.from_price_string(course_data[9]),
                        location=SportCourseLocation.from_pattern(data["orte"][course_data[6][0]]),
                        category_id=course_data[12],
                        status_code=course_data[0],
                        is_available=course_data[10] != 0,  # 0 seems to indicate availability
                    )

                    # Group courses by title
                    if title not in course_dict:
                        course_dict[title] = []
                    course_dict[title].append(course)

                except Exception as e:
                    logger.error(f"Failed to parse course {course_id}: {str(e)}")
                    continue

            # Create SportCourse objects from the grouped courses
            sport_courses = [SportCourse(title=title, courses=courses) for title, courses in course_dict.items()]

            logger.info(
                f"Found {len(sport_courses)} sport types with {sum(len(sc.courses) for sc in sport_courses)} total courses"
            )
            return sport_courses

        except requests.RequestException as e:
            logger.error(f"Error fetching courses: {str(e)}")
            return []


if __name__ == "__main__":
    crawler = ZhsCrawler()

    # Get all courses
    sport_courses = crawler.get_courses()

    # Print some course info
    for sport in sport_courses[:8]:  # Print first 5 sport types
        print(f"\nSport: {sport.title}")
        print(f"Number of courses: {len(sport.courses)}")
        for course in sport.courses[:10]:  # Print first 2 courses of each sport
            print(f"\n  Course: {course.name}")
            print("  Time slots:")
            for slot in course.time_slots:
                print(f"    {slot.day}: {slot.start_time}-{slot.end_time}")
            print(f"  Duration: {course.duration.start_date.date()} to {course.duration.end_date.date()}")
            print(f"  Price: {course.price.student}€ (Student)")
            print(f"  Available: {course.is_available}")
            print(f"  Location: {course.location.address}")
