import json
import re
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from data_fetcher.src.sport.models.sport_models import SportCourse
from shared.src.core.logging import get_sport_fetcher_logger

logger = get_sport_fetcher_logger(__name__)


class ZhsCrawler:
    def __init__(self):
        self.base_url = "https://kurse.zhs-muenchen.de"
        self.main_page_url = f"{self.base_url}/de/muenchen"
        self.multi_search_url = f"{self.base_url}/services/search/multi-search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.meilisearch_token = None

    def _load_main_page_and_get_token(self) -> str:
        """Load the main page and extract the meilisearch token"""
        try:
            logger.info("Loading main page to get authentication token...")
            response = self.session.get(self.main_page_url, headers=self.headers)
            response.raise_for_status()

            # Parse HTML to extract meilisearch token
            soup = BeautifulSoup(response.text, "html.parser")

            # Look for window.UniNow.MEILISEARCH_API_KEY in script tags
            for script in soup.find_all("script"):
                # Try both .string and .get_text() to get script content
                script_text = script.string or script.get_text()
                if script_text and "MEILISEARCH_API_KEY" in script_text:
                    # Extract the API key from the JavaScript
                    match = re.search(r'MEILISEARCH_API_KEY:\s*"([^"]+)"', script_text)
                    if match:
                        token = match.group(1)
                        logger.info(f"Found MEILISEARCH_API_KEY (length: {len(token)})")
                        return token

            # Try to find the token in x-data attributes (alternative location)
            for element in soup.find_all(attrs={"x-data": True}):
                x_data = element.get("x-data", "")
                if "meilisearch_token" in x_data:
                    # Extract JSON from x-data (it's HTML-encoded)
                    x_data = x_data.replace("&#34;", '"')
                    match = re.search(r"\{.*\}", x_data, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(0))
                            token = data.get("authentication", {}).get("meilisearch_token", "")
                            if token:
                                logger.info("Found meilisearch token in x-data")
                                return token
                        except json.JSONDecodeError:
                            continue

            logger.warning("No meilisearch token found, will try without it")
            return ""

        except requests.RequestException as e:
            logger.error(f"Error loading main page: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Error extracting token: {str(e)}")
            return ""

    def _fetch_offers_list(self) -> List[Dict[str, Any]]:
        """Fetch list of all sport offers from multi-search API"""
        try:
            # Ensure we have loaded the main page and have the token
            if not self.meilisearch_token:
                self.meilisearch_token = self._load_main_page_and_get_token()

            payload = {
                "queries": [
                    {
                        "indexUid": "public_offers_DE_de",
                        "q": "",
                        "limit": 1000,
                    }
                ]
            }

            # Add authorization header if we have a token
            headers = self.headers.copy()
            if self.meilisearch_token:
                headers["Authorization"] = f"Bearer {self.meilisearch_token}"

            response = self.session.post(self.multi_search_url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()

            if not data.get("results") or not data["results"][0].get("hits"):
                logger.error("No results found in multi-search response")
                return []

            all_offers = data["results"][0]["hits"]

            # Filter to only get course-offer type (not product-offer)
            offers = [offer for offer in all_offers if offer.get("type") == "course-offer"]

            logger.info(f"Found {len(offers)} course offers from multi-search API (out of {len(all_offers)} total)")
            return offers

        except requests.RequestException as e:
            logger.error(f"Error fetching offers list: {str(e)}")
            return []
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing offers list: {str(e)}")
            return []

    def _fetch_offer_details(self, slug: str) -> Dict[str, Any]:
        """Fetch detailed course information for a specific offer

        Args:
            slug: The offer slug (e.g., 'acrobatics')
        """
        try:
            # Construct the detail page URL
            # Default group slug based on the web search results
            group_slug = (
                "Sports%20courses%20in%20Munich%20as%20well%20as%20external%20locations%20and%20outdoor%20destinations"
            )
            detail_url = f"{self.base_url}/courses/{group_slug}/offers/{slug}"

            response = self.session.get(detail_url, headers=self.headers)
            response.raise_for_status()

            # Parse HTML to extract x-data attribute
            soup = BeautifulSoup(response.text, "html.parser")
            offer_details = soup.find(id="offer_details")

            if not offer_details:
                logger.error(f"Could not find #offer_details element for {slug}")
                return {}

            x_data = offer_details.get("x-data", "")
            if not x_data:
                logger.error(f"No x-data attribute found for {slug}")
                return {}

            # Extract JSON from x-data attribute
            # The x-data contains a JSON object, we need to extract it
            # Format: x-data="{...json...}"

            # Try to extract the JSON object
            match = re.search(r"\{.*\}", x_data, re.DOTALL)
            if not match:
                logger.error(f"Could not extract JSON from x-data for {slug}")
                return {}

            json_str = match.group(0)
            data = json.loads(json_str)

            return data

        except requests.RequestException as e:
            logger.error(f"Error fetching offer details for {slug}: {str(e)}")
            return {}
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Error parsing offer details for {slug}: {str(e)}")
            return {}

    def get_courses(self, exclude_keywords: List[str] = None) -> List[SportCourse]:
        """
        Fetch all courses from the ZHS website

        Args:
            exclude_keywords: List of keywords to filter out courses (case-insensitive)

        Returns:
            List of SportCourse objects
        """
        try:
            # Step 1: Fetch list of all offers
            offers = self._fetch_offers_list()

            if not offers:
                logger.error("No offers found")
                return []

            sport_courses = []

            # Step 2: Fetch details for each offer
            for offer in offers:
                offer_name = offer.get("name", "")
                offer_slug = offer.get("slug", "")

                # Skip if offer name contains any excluded keywords
                if exclude_keywords and any(keyword.lower() in offer_name.lower() for keyword in exclude_keywords):
                    logger.info(f"Skipping {offer_name} due to exclude keywords")
                    continue

                if not offer_slug:
                    logger.warning(f"No slug found for offer: {offer_name}")
                    continue

                logger.info(f"Fetching details for: {offer_name}")

                # Fetch detailed course data
                details = self._fetch_offer_details(offer_slug)

                if not details or "data" not in details:
                    logger.warning(f"No details found for {offer_name}")
                    continue

                data = details["data"]
                courses_data = data.get("courses", [])

                if not courses_data:
                    logger.warning(f"No courses found for {offer_name}")
                    continue

                # Create SportCourse from offer data
                try:
                    sport_course = SportCourse.from_offer_data(offer, courses_data)
                    if sport_course.courses:  # Only add if there are valid courses
                        sport_courses.append(sport_course)
                except Exception as e:
                    logger.error(f"Failed to create SportCourse for {offer_name}: {str(e)}")
                    continue

            logger.info(
                f"Found {len(sport_courses)} sport types with {sum(len(sc.courses) for sc in sport_courses)} total courses"
            )
            return sport_courses

        except Exception as e:
            logger.error(f"Error fetching courses: {str(e)}")
            return []


if __name__ == "__main__":
    crawler = ZhsCrawler()

    # Get all courses
    sport_courses = crawler.get_courses()

    # Print some course info
    for sport in sport_courses[:5]:  # Print first 5 sport types
        print(f"\nSport: {sport.title}")
        print(f"Number of courses: {len(sport.courses)}")
        for course in sport.courses[:2]:  # Print first 2 courses of each sport
            print(f"\n  Course: {course.name}")
            print("  Time slots:")
            for slot in course.time_slots:
                print(f"    {slot.day}: {slot.start_time}-{slot.end_time}")
            print(f"  Duration: {course.duration.start_date.date()} to {course.duration.end_date.date()}")
            print(f"  Price: {course.price.student}€ (Student)")
            print(f"  Available: {course.is_available}")
            if course.location:
                print(f"  Location: {course.location.address}")
