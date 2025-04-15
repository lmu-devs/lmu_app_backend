import re
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.enums import CinemaEnum, UniversityEnum

from ..constants.location_constants import CinemaLocationConstants
from ..constants.url_constants import HM_CINEMA_URL
from ..models.screening_model import ScreeningCrawl

logger = get_cinema_fetcher_logger(__name__)


class HmScreeningCrawler:
    def __init__(self):
        self.cinema_id = CinemaEnum.HM
        self.university_id = UniversityEnum.HM
        self.base_url = HM_CINEMA_URL
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.external_link = HM_CINEMA_URL
        self.price = 2.0
        self.is_edge_case = True

    def _parse_date_time(self, date_str: str, time_str: str) -> datetime | None:
        """Convert date and time strings to datetime object"""
        try:
            date_match = re.match(r"\w+ (\d{2})\.(\d{2})\.(\d{4})", date_str)
            if not date_match:
                logger.warning(f"Could not parse date string: {date_str}")
                return None

            day, month, year = date_match.groups()
            # Parse time (format: "19:00")
            hour, minute = map(int, time_str.split(":"))
            return datetime(int(year), int(month), int(day), hour, minute)
        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing date/time: {date_str} {time_str} - {str(e)}")
            return None

    def _extract_screenings(self, html_content: str) -> List[ScreeningCrawl]:
        """Extract screening information from HTML content"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            screenings = []

            # Find all film rows in the current semester program
            showcase_rows = soup.select(".film-showcase")

            if not showcase_rows:
                logger.warning("No film rows found in HTML content")
                return []

            for showcase in showcase_rows:
                try:
                    # Extract image URL
                    image_tag = showcase.find("img")
                    custom_poster_url = f"https://www.unifilm.de/{image_tag['src']}" if image_tag else None

                    # Extract description and tagline
                    text_container = showcase.find("div", class_="text_container")
                    description_parts = []
                    note = None
                    if text_container:
                        # Extract tagline from the standalone span (not within p tags)
                        tagline_span = text_container.find(
                            "span", recursive=False
                        )  # recursive=False to only get direct children
                        if tagline_span:
                            note = tagline_span.get_text(strip=True)

                        # Extract description from p tags
                        paragraphs = text_container.find_all("p")
                        for p in paragraphs:
                            description_parts.append(p.get_text(strip=True))
                    overview = " ".join(description_parts)

                    # Extract runtime
                    film_data = showcase.find("ul", class_="film-info-filmdaten")
                    runtime = None
                    if film_data:
                        for li in film_data.find_all("li"):
                            if "Min." in li.get_text():
                                runtime = int(li.get_text().replace(" Min.", "").strip())

                    # Extract basic information
                    date = showcase.select_one(".film-info-text.datum")
                    time = showcase.select_one(".film-info-text.uhrzeit")
                    title = showcase.select_one("h1.headline-h3 span")

                    if not all([date, time, title]):
                        logger.warning(f"Missing required information in row: {showcase}")
                        continue

                    date = date.text.strip()
                    time = time.text.replace("Uhr", "").strip()
                    title = title.text.strip()

                    # Parse datetime
                    screening_datetime = self._parse_date_time(date, time)
                    if not screening_datetime:
                        continue

                    # Check if it's an OV/OmU screening
                    is_ov = False
                    subtitles = None
                    if "[OV]" in title:
                        is_ov = True
                        title = title.replace("[OV]", "").strip()
                    elif "[OmU]" in title:
                        is_ov = True
                        subtitles = "OmU"
                        title = title.replace("[OmU]", "").strip()
                    elif "[OmeU]" in title:
                        is_ov = True
                        subtitles = "OmeU"
                        title = title.replace("[OmeU]", "").strip()

                    # Remove other tags from title
                    title = re.sub(r"\[.*?\]", "", title).strip()

                    # Check if it's a special screening with free entrance
                    if any(
                        text in note
                        for text in [
                            "Gratis Eintritt",
                            "Freier Eintritt",
                            "gratis",
                            "kostenlos",
                        ]
                    ):
                        self.price = 0.0

                    location = CinemaLocationConstants[self.cinema_id]

                    # Create ScreeningCrawl object
                    screening = ScreeningCrawl(
                        is_edge_case=self.is_edge_case,
                        date=screening_datetime,
                        title=title,
                        address=location.address,
                        longitude=location.longitude,
                        latitude=location.latitude,
                        is_ov=is_ov,
                        price=self.price,
                        subtitles=subtitles,
                        cinema_id=self.cinema_id,
                        university_id=self.university_id,
                        external_url=self.external_link,
                        custom_poster_url=custom_poster_url,
                        overview=overview,
                        runtime=runtime,
                        note=note,
                    )
                    screenings.append(screening)

                except Exception as e:
                    logger.error(f"Error processing row: {str(e)}")
                    continue

            return screenings

        except Exception as e:
            logger.error(f"Error extracting screenings: {str(e)}")
            return []

    def crawl(self) -> List[ScreeningCrawl]:
        """Fetch and parse the cinema program"""
        try:
            # Make HTTP request
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Check if response is valid
            if not response.text:
                logger.error("Empty response received from server")
                return []

            return self._extract_screenings(response.text)

        except requests.RequestException as e:
            logger.error(f"Error fetching data from {self.base_url}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during crawl: {str(e)}")
            return []


if __name__ == "__main__":
    crawler = HmScreeningCrawler()
    for screening in crawler.crawl():
        print("--------------------------------\n")
        print(screening.__dict__)
    print("Number of screenings: ", len(crawler.crawl()))
