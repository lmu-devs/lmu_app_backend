import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
import re
import logging

from shared.enums.university_enums import UniversityEnum
from data_fetcher.cinema.models.movie_model import ScreeningCrawl

logger = logging.getLogger(__name__)

class HMCinemaCrawler:
    def __init__(self):
        self.base_url = "https://www.unifilm.de/studentenkinos/muenchen_hm"
        self.address = "Hörsaal E0.103 - Tram Station Lothstraße"
        self.longitude = 11.554943
        self.latitude = 48.153699
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.university_id = UniversityEnum.HM.value
        self.external_link = "https://www.unifilm.de/studentenkinos/muenchen_hm"
        self.price = 3.5

    def _parse_date_time(self, date_str: str, time_str: str) -> datetime | None:
        """Convert date and time strings to datetime object"""
        try:
            # Convert German date format to datetime
            date_match = re.match(r'Do\. (\d{2})\.(\d{2})\.(\d{4})', date_str)
            if not date_match:
                logger.warning(f"Could not parse date string: {date_str}")
                return None
                
            day, month, year = date_match.groups()
            # Parse time (format: "19:00")
            hour, minute = map(int, time_str.split(':'))
            return datetime(int(year), int(month), int(day), hour, minute)
        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing date/time: {date_str} {time_str} - {str(e)}")
            return None

    def _extract_screenings(self, html_content: str) -> List[ScreeningCrawl]:
        """Extract screening information from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            screenings = []

            # Find all film rows in the current semester program
            film_rows = soup.select('.spielplan-thisSemester .semester-film-row')
            
            if not film_rows:
                logger.warning("No film rows found in HTML content")
                return []

            for row in film_rows:
                try:
                    # Extract basic information
                    date = row.select_one('.film-row-datum')
                    time = row.select_one('.film-row-uhrzeit')
                    title = row.select_one('.film-row-titel')
                    info = row.select_one('.film-row-info')

                    if not all([date, time, title]):
                        logger.warning(f"Missing required information in row: {row}")
                        continue

                    date = date.text.strip()
                    time = time.text.replace('Uhr', '').strip()
                    title = title.text.strip()
                    info = info.text.strip() if info else None

                    # Parse datetime
                    screening_datetime = self._parse_date_time(date, time)
                    if not screening_datetime:
                        continue

                    # Check if it's an OV/OmU screening
                    is_ov = False
                    subtitles = None
                    if '[OV]' in title:
                        is_ov = True
                        title = title.replace('[OV]', '').strip()
                    elif '[OmU]' in title:
                        subtitles = 'OmU'
                        title = title.replace('[OmU]', '').strip()
                    elif '[OmeU]' in title:
                        subtitles = 'OmeU'
                        title = title.replace('[OmeU]', '').strip()
                    
                    # Remove other tags from title
                    title = re.sub(r'\[.*?\]', '', title).strip()
                    
                    # Check if it's a special screening with free entrance
                    price = None
                    if info and any(text in info for text in ['Gratis Eintritt', 'Freier Eintritt', 'gratis', 'kostenlos']):
                        price = 0.0

                    # Get additional info from movie details if available
                    movie_id = row.get('data-id')
                    year = None

                    # Create ScreeningCrawl object
                    screening = ScreeningCrawl(
                        date=screening_datetime,
                        title=title,
                        address=self.address,
                        longitude=self.longitude,
                        latitude=self.latitude,
                        is_ov=is_ov,
                        price=price,
                        subtitles=subtitles,
                        university_id=self.university_id,
                        year=year,
                        external_link=self.external_link
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
    crawler = HMCinemaCrawler()
    for screening in crawler.crawl():
        print(screening.__dict__)

