import re
import requests

from datetime import datetime
from bs4 import BeautifulSoup

from shared.enums.university_enums import UniversityEnum
from shared.core.logging import get_movie_fetcher_logger
from ..models.movie_model import ScreeningCrawl

# Initialize logger
logger = get_movie_fetcher_logger(__name__)


class TumMovieCrawler:
    def __init__(self):
        self.university_id = UniversityEnum.TUM.value
        self.base_url = "https://www.tu-film.de/programm/index/upcoming.rss"
        
    def _parse_date(date_str) -> datetime:
        """Convert date string to datetime"""
        try:
            # Convert date string to datetime
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return date_obj
        except ValueError as e:
            logger.error(f"Failed to parse date {date_str}: {e}")
            return None

    def _clean_title(title: str) -> str:
        """Clean the title by removing date and parenthetical information"""
        # Remove date pattern (e.g., "3. 12. 2024: ")
        title = re.sub(r'^\d+\.\s*\d+\.\s*\d+:\s*', '', title)
        
        # Remove content in parentheses at the end (e.g., "(Garching)", "(OV)")
        title = re.sub(r'\s*\([^)]*\)\s*$', '', title)
        
        return title.strip()

    def _extract_year_from_text(text: str) -> int | None:
        """Extract year from text, handling parentheses"""
        if not text:
            return None
        
        # Remove parentheses and convert to int
        year_str = text.strip('() ')
        try:
            return int(year_str)
        except ValueError:
            return None



    def crawl(self) -> list[ScreeningCrawl]:
        response = requests.get(self.base_url)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch the RSS feed, status code: {response.status_code}")
            return []
        
        logger.info("Successfully fetched TUM movie RSS feed")
        soup = BeautifulSoup(response.content, 'xml')
        
        
        movies = []
        for item in soup.find_all('item'):
            title = self._clean_title(item.title.text)
            
            # Skip surprise movies
            if "berraschungsfilm" in title:
                movies.append(ScreeningCrawl(
                    date=self._parse_date(item.pubDate.text),
                    title=title,
                    external_link=item.link.text,
                    price=0 if "Free Entrance" in title else 3.3,
                    university_id=self.university_id,
                    is_ov="OV" in title,
                    address=item.find('location').text if item.find('location') else None,
                    longitude=0,
                    latitude=0
                ))
                logger.info("Added surprise movie entry")
                continue

            
            movies.append(ScreeningCrawl(
                date=self._parse_date(item.pubDate.text),
                title=title,
                year=self._extract_year_from_text(title),
                external_link=item.link.text,
                price=0 if "Free Entrance" in title else 3.3,
                university_id=self.university_id,
                is_ov="OV" in title,
                subtitles="OmdU" if "OmdU" in title else "OmeU" if "OmeU" in title else None,
                address=item.find('location').text if item.find('location') else None,
                longitude=0,
                latitude=0
                
            ))
            logger.info(f"Successfully parsed movie: {title})")
        
        logger.info(f"Found {len(movies)} movies in total")
        return movies[0:5]

