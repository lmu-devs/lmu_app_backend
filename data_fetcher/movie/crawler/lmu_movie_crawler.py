import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from data_fetcher.movie.models.movie_model import LmuMovie
from shared.core.logging import get_movie_fetcher_logger

# Initialize logger
logger = get_movie_fetcher_logger(__name__)



def parse_date(date_str) -> datetime:
    """Convert date string to datetime at 20:00"""
    try:
        # Convert DD.MM.YY to datetime at 20:00
        date_obj = datetime.strptime(date_str, '%d.%m.%y')
        return date_obj.replace(hour=20)
    except ValueError as e:
        logger.error(f"Failed to parse date {date_str}: {e}")
        return None

def crawl_lmu_movie_data() -> list[LmuMovie]:
    url = "https://u-kino.de/programm/"
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch the page, status code: {response.status_code}")
        return []
    
    logger.info("Successfully fetched LMU movie page")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the first ul in the main content area
    content_area = soup.find('div', id='primary')
    if not content_area:
        logger.error("Could not find the main content area")
        return []
    
    movie_list = content_area.find('ul')
    if not movie_list:
        logger.error("Could not find movie list")
        return []
    
    movies = []
    for item in movie_list.find_all('li'):
        text = item.get_text().strip()
        logger.debug(f"Processing movie item: {text}")
        
        # Handle surprise movie case
        if '[Surprise Movie]' in text:
            match = re.match(r"(\d{2}\.\d{2}\.\d{2}):", text)
            if match:
                movies.append(LmuMovie(
                    date=parse_date(match.group(1)),
                    title="Surprise Movie",
                    aka_name=None,
                    year=None
                ))
                logger.info("Added surprise movie entry")
            continue
        
        # Regular movie pattern
        pattern = r"(\d{2}\.\d{2}\.\d{2}):\s*(.*?)(?:\s+aka\s+(.*?))?\s*\(R:.*?,\s*(\d{4})\)"
        match = re.match(pattern, text)
        
        if match:
            date_str, title, aka_name, year = match.groups()
            movies.append(LmuMovie(
                date=parse_date(date_str),
                title=title.strip(),
                aka_name=aka_name.strip() if aka_name else None,
                year=int(year)
            ))
            logger.info(f"Successfully parsed movie: {title} ({year})")
        else:
            logger.warning(f"Could not parse movie entry: {text}")
    
    logger.info(f"Found {len(movies)} movies in total")
    return movies[0:5]

