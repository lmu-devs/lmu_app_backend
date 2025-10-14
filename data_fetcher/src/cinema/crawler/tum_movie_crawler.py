import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from data_fetcher.src.cinema.constants.url_constants import TUM_CINEMA_URL
from data_fetcher.src.cinema.models.screening_model import ScreeningCrawl
from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.enums import CinemaEnum, UniversityEnum

logger = get_cinema_fetcher_logger(__name__)


class TumScreeningCrawler:
    def __init__(self):
        self.cinema_id = None
        self.university_id = UniversityEnum.TUM
        self.base_url = TUM_CINEMA_URL.rstrip("/")
        self.rss_url = f"{self.base_url}/programm/index/upcoming.rss"
        self.booking_url = f"{self.base_url}/pages/view/kinoheld"
        self.price = 3.3
        self.longitude = None
        self.latitude = None

    def _parse_date(self, date_str) -> datetime:
        try:
            date_str = date_str.rsplit(" ", 1)[0]
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
        except ValueError as e:
            logger.error(f"Failed to parse date {date_str}: {e}")
            return None

    def _clean_title(self, title: str) -> str:
        title = re.sub(r"^\d+\.\s*\d+\.\s*\d+:\s*", "", title)
        title = re.sub(r"\s*\([^)]*\)\s*$", "", title)
        return title.strip()

    def _clean_html_description(self, html_text: str) -> str:
        if not html_text:
            return None

        soup = BeautifulSoup(html_text, "html.parser")
        paragraphs = soup.find_all("p")

        if paragraphs:
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            text = soup.get_text(strip=True)

        return text if text else None

    def _fetch_movie_details(self, external_link: str) -> BeautifulSoup | None:
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
        try:
            h4_text = soup.find("h4")
            if not h4_text:
                logger.warning("Could not find h4 tag with year information")
                return None

            year_match = re.search(r"\((\d{4})\)", h4_text.text)
            return int(year_match.group(1)) if year_match else None
        except Exception as e:
            logger.error(f"Error extracting year: {e}")
            return None

    def _extract_poster_url(self, soup: BeautifulSoup) -> str | None:
        try:
            img_tag = soup.find("img", class_="poster")
            if img_tag and "src" in img_tag.attrs:
                return f"{self.base_url}{img_tag['src']}"
            return None
        except Exception as e:
            logger.error(f"Error extracting poster URL: {e}")
            return None

    def _extract_tagline(self, soup: BeautifulSoup) -> str | None:
        try:
            teaser_div = soup.find("div", class_="teaser")
            return teaser_div.text.strip() if teaser_div else None
        except Exception as e:
            logger.error(f"Error extracting tagline: {e}")
            return None

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        try:
            description_div = soup.find("div", class_="description")
            if description_div:
                paragraphs = description_div.find_all("p")
                return "\n\n".join(p.text.strip() for p in paragraphs)
            return None
        except Exception as e:
            logger.error(f"Error extracting description: {e}")
            return None

    def _get_movie_details(self, external_link: str) -> tuple[int | None, str | None, str | None, str | None]:
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

    def _extract_poster_from_rss(self, item) -> str | None:
        try:
            enclosure = item.find("enclosure")
            if enclosure and enclosure.get("url"):
                poster_url = enclosure.get("url")
                if not poster_url.startswith("http"):
                    poster_url = f"{self.base_url}{poster_url}"
                return poster_url
            return None
        except Exception as e:
            logger.error(f"Error extracting poster from RSS: {e}")
            return None

    def _extract_description_from_rss(self, item) -> str | None:
        try:
            description_tag = item.find("description")
            if description_tag and description_tag.text:
                return self._clean_html_description(description_tag.text)
            return None
        except Exception as e:
            logger.error(f"Error extracting description from RSS: {e}")
            return None

    def crawl(self) -> list[ScreeningCrawl]:
        response = requests.get(self.rss_url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch the RSS feed, status code: {response.status_code}")
            return []

        logger.info("Successfully fetched TUM movie RSS feed")
        soup = BeautifulSoup(response.content, "html.parser")

        movies = []
        for item in soup.find_all("item"):
            try:
                if not item.title or not item.title.text:
                    logger.warning("Item has no title, skipping")
                    continue

                base_title = item.title.text
                pubdate_tag = item.find("pubdate")
                location_tag = item.find("location")
                guid_tag = item.find("guid")

                if not pubdate_tag or not pubdate_tag.text:
                    logger.warning(f"No pubdate found for movie: {base_title}, skipping")
                    continue

                if not location_tag or not location_tag.text:
                    logger.warning(f"No location tag found for movie: {base_title}, skipping")
                    continue

                if not guid_tag or not guid_tag.text:
                    logger.warning(f"No guid found for movie: {base_title}, skipping")
                    continue

                is_garching = "Garching" in location_tag.text
                self.cinema_id = CinemaEnum.TUM_GARCHING.value if is_garching else CinemaEnum.TUM.value

                title = self._clean_title(base_title)
                date = self._parse_date(pubdate_tag.text)
                external_link = guid_tag.text

                rss_poster_url = self._extract_poster_from_rss(item)
                rss_description = self._extract_description_from_rss(item)

                year, detail_poster_url, tagline, detail_description = self._get_movie_details(external_link)

                custom_poster_url = rss_poster_url or detail_poster_url
                description = rss_description or detail_description

                is_edge_case = year is None
                price = 0 if "Free Entrance" in base_title else self.price
                is_ov = "OV" in base_title
                subtitles = "OmdU" if "OmdU" in base_title else "OmeU" if "OmeU" in base_title else None

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
                        address=location_tag.text,
                        longitude=self.longitude,
                        latitude=self.latitude,
                        custom_poster_url=custom_poster_url,
                        tagline=tagline,
                        overview=description,
                    )
                )
                logger.info(f"Successfully parsed movie: {title}")
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                continue

        logger.info(f"Found {len(movies)} movies in total")
        return movies


if __name__ == "__main__":
    crawler = TumScreeningCrawler()
    screenings = crawler.crawl()
    for screening in screenings:
        print("--------------------------------")
        print(screening.__dict__)
    print(f"\nTotal screenings: {len(screenings)}")
