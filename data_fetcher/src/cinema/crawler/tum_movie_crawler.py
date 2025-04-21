import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from data_fetcher.src.cinema.constants.url_constants import TUM_CINEMA_URL
from data_fetcher.src.cinema.models.screening_model import ScreeningCrawl
from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.enums import CinemaEnum, UniversityEnum

# Initialize logger
logger = get_cinema_fetcher_logger(__name__)


class TumScreeningCrawler:
    def __init__(self):
        self.cinema_id = None
        self.university_id = UniversityEnum.TUM
        self.base_url = TUM_CINEMA_URL
        self.rss_url = f"{self.base_url}/programm/index/upcoming.rss"
        self.booking_url = f"{self.base_url}/pages/view/kinoheld"
        self.price = 3.3
        self.longitude = None
        self.latitude = None

    def _parse_date(self, date_str) -> datetime:
        """Convert date string to datetime"""
        try:
            # Remove timezone part and parse
            date_str = date_str.rsplit(" ", 1)[0]  # Remove last part (the +0100)
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
        except ValueError as e:
            logger.error(f"Failed to parse date {date_str}: {e}")
            return None

    def _clean_title(self, title: str) -> str:
        """Clean the title by removing date and parenthetical information"""
        # Remove date pattern (e.g., "3. 12. 2024: ")
        title = re.sub(r"^\d+\.\s*\d+\.\s*\d+:\s*", "", title)

        # Remove content in parentheses at the end (e.g., "(Garching)", "(OV)")
        title = re.sub(r"\s*\([^)]*\)\s*$", "", title)

        return title.strip()

    def _fetch_movie_details(self, external_link: str) -> BeautifulSoup | None:
        """Fetch and parse the movie's detail page"""
        try:
            response = requests.get(external_link)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch movie details from {external_link}")
                return None

            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"Error fetching movie details: {e}")
            return None

    def _extract_year(self, soup: BeautifulSoup) -> int | None:
        """Extract year from movie details soup"""
        try:
            h4_text = soup.find("h4")
            if not h4_text:
                logger.warning("Could not find h4 tag with year information")
                return None

            year_match = re.search(r"\((\d{4})\)", h4_text.text)
            if year_match:
                return int(year_match.group(1))
            return None
        except Exception as e:
            logger.error(f"Error extracting year: {e}")
            return None

    def _extract_poster_url(self, soup: BeautifulSoup) -> str | None:
        """Extract custom poster URL from movie details soup"""
        try:
            img_tag = soup.find("img", class_="poster")
            if img_tag and "src" in img_tag.attrs:
                return f"{self.base_url}{img_tag['src']}"
            return None
        except Exception as e:
            logger.error(f"Error extracting poster URL: {e}")
            return None

    def _extract_tagline(self, soup: BeautifulSoup) -> str | None:
        """Extract tagline (teaser) from movie details soup"""
        try:
            teaser_div = soup.find("div", class_="teaser")
            if teaser_div:
                return teaser_div.text.strip()
            return None
        except Exception as e:
            logger.error(f"Error extracting tagline: {e}")
            return None

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        """Extract description from movie details soup"""
        try:
            description_div = soup.find("div", class_="description")
            if description_div:
                # Combine all paragraphs into one string, preserving paragraph breaks
                paragraphs = description_div.find_all("p")
                description = "\n\n".join(p.text.strip() for p in paragraphs)
                return description
            return None
        except Exception as e:
            logger.error(f"Error extracting description: {e}")
            return None

    def _get_movie_details(self, external_link: str) -> tuple[int | None, str | None, str | None, str | None]:
        """Get year, custom poster URL, tagline, and description from movie's detail page"""
        soup = self._fetch_movie_details(external_link)
        if not soup:
            return None, None, None, None

        year = self._extract_year(soup)
        custom_poster_url = None
        tagline = None
        description = None

        if not year:
            custom_poster_url = self._extract_poster_url(soup)
            tagline = self._extract_tagline(soup)
            description = self._extract_description(soup)

        return year, custom_poster_url, tagline, description

    def _is_garching_in_location(self, location: str) -> bool:
        return "Garching" in location

    def crawl(self) -> list[ScreeningCrawl]:
        response = requests.get(self.rss_url)

        if response.status_code != 200:
            logger.error(f"Failed to fetch the RSS feed, status code: {response.status_code}")
            return []

        logger.info("Successfully fetched TUM movie RSS feed")
        soup = BeautifulSoup(response.content, "xml")

        movies = []
        for item in soup.find_all("item"):
            base_title = item.title.text

            is_garching = self._is_garching_in_location(item.find("location").text)
            self.cinema_id = CinemaEnum.TUM_GARCHING.value if is_garching else CinemaEnum.TUM.value
            title = self._clean_title(base_title)
            date = self._parse_date(item.pubDate.text)
            external_link = item.link.text
            year, custom_poster_url, tagline, description = self._get_movie_details(external_link)
            is_edge_case = year is None
            price = 0 if "Free Entrance" in base_title else self.price
            is_ov = "OV" in base_title
            subtitles = "OmdU" if "OmdU" in base_title else "OmeU" if "OmeU" in base_title else None
            address = item.find("location").text if item.find("location") else None

            movies.append(
                ScreeningCrawl(
                    is_edge_case=is_edge_case,
                    date=date,
                    title=title,
                    year=year,
                    external_url=external_link,
                    booking_url=self.booking_url,
                    price=price,
                    cinema_id=self.cinema_id,
                    university_id=self.university_id,
                    is_ov=is_ov,
                    subtitles=subtitles,
                    address=address,
                    longitude=self.longitude,
                    latitude=self.latitude,
                    custom_poster_url=custom_poster_url,
                    tagline=tagline,
                    overview=description,
                )
            )
            logger.info(f"Successfully parsed movie: {title}")

        logger.info(f"Found {len(movies)} movies in total")
        return movies


if __name__ == "__main__":
    crawler = TumScreeningCrawler()
    for screening in crawler.crawl():
        print("--------------------------------\n")
        print(screening.__dict__)
    print("Number of screenings: ", len(crawler.crawl()))
