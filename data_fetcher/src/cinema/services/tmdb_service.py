from typing import Any, Dict, List, Optional

import requests

from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.enums import LanguageEnum

settings = get_settings()
logger = get_cinema_fetcher_logger(__name__)


class TmdbService:
    def __init__(self) -> None:
        self.tmdb_headers = {
            "Authorization": f"Bearer {settings.TMDB_API_KEY}",
            "accept": "application/json",
        }
        self.tmdb_base_url = "https://api.themoviedb.org/3"

    def search_tmdb_movie(self, title: str, year: str) -> Optional[Dict[Any, Any]]:
        """Search for a movie on TMDB and get its details in all languages"""
        try:
            # Step 1: Search for the movie
            search_url = f"{self.tmdb_base_url}/search/movie"
            search_params = {
                "query": title,
                "language": LanguageEnum.ENGLISH_US.value,
                "page": 1,
            }
            if year:
                search_params["year"] = year

            search_response = requests.get(search_url, params=search_params, headers=self.tmdb_headers)
            search_response.raise_for_status()

            results = search_response.json().get("results", [])
            if not results:
                logger.warning(f"No results found for movie: {title} ({year})")
                return None

            # Get the first result's ID
            movie_id = results[0]["id"]
            logger.info(f"Found movie ID {movie_id} for {title}")

            # Step 2: Get detailed movie info for all languages
            movie_data = {}
            for lang in LanguageEnum:
                details_url = f"{self.tmdb_base_url}/movie/{movie_id}"
                params = {
                    "language": lang.value.lower(),
                    "append_to_response": "external_ids,videos",
                }

                details_response = requests.get(details_url, params=params, headers=self.tmdb_headers)
                details_response.raise_for_status()
                movie_data[lang] = details_response.json()
                logger.debug(f"Retrieved {lang.value} data for movie {title}")

            return movie_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching TMDB data for {title}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing TMDB data for {title}: {e}")
            return None
