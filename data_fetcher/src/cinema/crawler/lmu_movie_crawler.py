import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from data_fetcher.src.cinema.constants.location_constants import CinemaLocationConstants
from data_fetcher.src.cinema.constants.url_constants import LMU_CINEMA_URL
from data_fetcher.src.cinema.models.screening_model import ScreeningCrawl
from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.enums import CinemaEnum, UniversityEnum

# Initialize logger
logger = get_cinema_fetcher_logger(__name__)


class LmuScreeningCrawler:
    def __init__(self):
        self.base_url = LMU_CINEMA_URL
        self.price = 3.5
        self.external_link = LMU_CINEMA_URL
        self.cinema_id = CinemaEnum.LMU
        self.university_id = UniversityEnum.LMU
        self.is_ov = True

    def _parse_date(self, date_str) -> datetime:
        """Convert date string to datetime at 20:00"""
        try:
            # Convert DD.MM.YY to datetime at 20:00
            date_obj = datetime.strptime(date_str, "%d.%m.%y")
            return date_obj.replace(hour=20)
        except ValueError as e:
            logger.error(f"Failed to parse date {date_str}: {e}")
            return None

    def crawl(self) -> list[ScreeningCrawl]:
        response = requests.get(f"{self.base_url}/programm")

        if response.status_code != 200:
            logger.error(f"Failed to fetch the page, status code: {response.status_code}")
            return []

        logger.info("Successfully fetched LMU movie page")
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the first ul in the main content area
        content_area = soup.find("div", id="primary")
        if not content_area:
            logger.error("Could not find the main content area")
            return []

        movie_list = content_area.find("ul")
        if not movie_list:
            logger.error("Could not find movie list")
            return []

        screenings = []
        for item in movie_list.find_all("li"):
            text = item.get_text()

            # Extract date and title using regex
            date_match = re.match(r"(\d{2}\.\d{2}\.\d{2}): (.+)", text)
            if not date_match:
                continue

            date_str, full_title = date_match.groups()
            date = self._parse_date(date_str)

            # Check if this is a nested movie (has a sub-list)
            if item.find("ul"):
                # For the main movie, only use the text before the nested list
                main_text = ""
                for content in item.contents:
                    if content.name == "ul":
                        break
                    if hasattr(content, "get_text"):
                        main_text += content.get_text()
                    else:
                        main_text += str(content)
                main_text = main_text.strip()

                date_match = re.match(r"(\d{2}\.\d{2}\.\d{2}): (.+)", main_text)
                if date_match:
                    _, full_title = date_match.groups()

            # Extract year and clean title
            year_match = re.search(r"\(.*?(\d{4})\)", full_title)
            year = int(year_match.group(1)) if year_match else None

            # Clean up title
            title = re.sub(r"\(R:.*?\d{4}\)", "", full_title)  # Remove director and year
            title = re.sub(r"aka.*$", "", title)  # Remove aka part
            title = title.strip()

            # Get aka name if exists
            aka_match = re.search(r"aka\s+(.+?)\s*(?:\(|$)", full_title)
            aka_name = aka_match.group(1).strip() if aka_match else None

            # Check if this is an edge case
            is_edge_case = year is None or "[" in title

            location = CinemaLocationConstants[self.cinema_id]

            screenings.append(
                ScreeningCrawl(
                    is_edge_case=is_edge_case,
                    title=title,
                    date=date,
                    aka_name=aka_name,
                    year=year,
                    is_ov=self.is_ov,
                    address=location.address,
                    longitude=location.longitude,
                    latitude=location.latitude,
                    external_url=self.external_link,
                    cinema_id=self.cinema_id,
                    university_id=self.university_id,
                    price=self.price,
                )
            )
            logger.info(f"Successfully parsed movie: {title} ({year})")

        logger.info(f"Found {len(screenings)} movies in total")
        return screenings


if __name__ == "__main__":
    crawler = LmuScreeningCrawler()
    for screening in crawler.crawl():
        print(screening.__dict__)
        print("--------------------------------\n")
