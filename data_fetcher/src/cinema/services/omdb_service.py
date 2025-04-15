from typing import Any, Dict, Optional

import requests

from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.core.settings import get_settings

settings = get_settings()
logger = get_cinema_fetcher_logger(__name__)


class OmdbService:
    def __init__(self):
        self.omdb_base_url = "http://www.omdbapi.com"
        self.omdb_api_key = settings.OMDB_API_KEY

    def get_omdb_data(self, imdb_id: str) -> Optional[Dict[Any, Any]]:
        """Get movie data from OMDB"""
        try:
            # Construct URL with proper format
            params = {"i": imdb_id, "apikey": self.omdb_api_key}
            response = requests.get(self.omdb_base_url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("Response") == "False":
                logger.warning(f"OMDB returned no data for {imdb_id}: {data.get('Error')}")
                return None

            logger.info(f"Successfully retrieved OMDB data for {imdb_id}")
            logger.debug(f"OMDB Ratings: {data.get('Ratings', [])}")
            return data

        except Exception as e:
            logger.error(f"Error fetching OMDB data for {imdb_id}: {e}")
            return None
