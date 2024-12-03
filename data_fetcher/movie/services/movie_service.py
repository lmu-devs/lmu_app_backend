import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests

from data_fetcher.movie.crawler.lmu_movie_crawler import crawl_lmu_movie_data
from data_fetcher.movie.models.movie_model import LmuMovie
from shared.core.logging import get_movie_fetcher_logger
from shared.enums.language_enums import Language
from shared.enums.rating_enums import RatingSource
from shared.enums.university_enums import University
from shared.tables.movie_table import (MovieLocationTable, MovieRatingTable, MovieScreeningTable,
                                       MovieTable, MovieTranslationTable, MovieTrailerTable, MovieTrailerTranslationTable)
from shared.settings import get_settings

settings = get_settings()
logger = get_movie_fetcher_logger(__name__)

class MovieService:
    def __init__(self):
        self.tmdb_headers = {
            'Authorization': f'Bearer {settings.TMDB_API_KEY}',
            'accept': 'application/json'
        }
        self.omdb_api_key = settings.OMDB_API_KEY
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.omdb_base_url = "http://www.omdbapi.com"

    def _search_tmdb_movie(self, title: str, year: str) -> Optional[Dict[Any, Any]]:
        """Search for a movie on TMDB and get its details in all languages"""
        try:
            # Step 1: Search for the movie
            search_url = f"{self.tmdb_base_url}/search/movie"
            search_params = {
                "query": title,
                "language": Language.ENGLISH_US.value,
                "page": 1
            }
            if year:
                search_params["year"] = year
            
            search_response = requests.get(
                search_url, 
                params=search_params,
                headers=self.tmdb_headers
            )
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
            for lang in Language:
                details_url = f"{self.tmdb_base_url}/movie/{movie_id}"
                params = {
                    "language": lang.value.lower(),
                    "append_to_response": "external_ids,videos"
                }
                
                details_response = requests.get(
                    details_url, 
                    params=params,
                    headers=self.tmdb_headers
                )
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

    def _get_omdb_data(self, imdb_id: str) -> Optional[Dict[Any, Any]]:
        """Get movie data from OMDB"""
        try:
            # Construct URL with proper format
            params = {
                "i": imdb_id,
                "apikey": self.omdb_api_key
            }
            response = requests.get(self.omdb_base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('Response') == 'False':
                logger.warning(f"OMDB returned no data for {imdb_id}: {data.get('Error')}")
                return None
                
            logger.info(f"Successfully retrieved OMDB data for {imdb_id}")
            logger.debug(f"OMDB Ratings: {data.get('Ratings', [])}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching OMDB data for {imdb_id}: {e}")
            return None

    def _normalize_rating(self, source: RatingSource, value: str) -> float:
        """Convert various rating formats to a 0-1 scale"""
        try:
            if source == RatingSource.IMDB:
                # IMDB: "8.3/10" -> 0.83
                return float(value.split('/')[0]) / 10
            elif source == RatingSource.ROTTEN_TOMATOES:
                # Rotten Tomatoes: "98%" -> 0.98
                return float(value.rstrip('%')) / 100
            elif source == RatingSource.METACRITIC:
                # Metacritic: "88/100" -> 0.88
                return float(value.split('/')[0]) / 100
        except (ValueError, IndexError) as e:
            logger.error(f"Error normalizing rating {value} for source {source}: {e}")
            return 0.0

    def _create_movie_model(self, tmdb_data: Dict[Any, Any], omdb_data: Dict[Any, Any], movie_data: LmuMovie) -> tuple[MovieTable, list[MovieTranslationTable], MovieScreeningTable, list[MovieRatingTable], list[MovieTrailerTable], list[MovieTrailerTranslationTable]]:
        """Create MovieTable and related instances from API data"""
        base_data = tmdb_data[Language.ENGLISH_US]  # Use English as base
    
        
        # Create main movie entry
        movie_id = uuid.uuid4()
        
        movie = MovieTable(
            id=movie_id,
            budget=base_data.get("budget", 0),
            imdb_id=base_data["external_ids"]["imdb_id"],
            popularity=base_data.get("popularity", 0.0),
            release_date=datetime.fromisoformat(base_data["release_date"]),
            runtime=base_data.get("runtime", 0),
            language=base_data.get("original_language", "en"),
            homepage=base_data.get("homepage", ""),
            original_title=base_data["original_title"],
        )
        
        # Create screenings
        # TODO: make this dynamic
        screening_id = uuid.uuid4()
        date = movie_data.date.replace(hour=20)
        end_time = date + timedelta(minutes=movie.runtime)
        entry_time = date - timedelta(minutes=30)
        address = "Hörsaal B052, Theresienstraße 37-39"
        longitude = 11.573249
        latitude = 48.147902
        
        screening = MovieScreeningTable(
            id=screening_id,
            movie_id=movie_id,
            date=date,
            university_id=University.LMU.value,
            start_time=date,
            end_time=end_time,
            entry_time=entry_time,
            location=MovieLocationTable(
                screening_id=screening_id,
                address=address,
                longitude=longitude,
                latitude=latitude
            )
        )

        # Create translations
        backdrop_path = base_data.get("backdrop_path", "")
        if backdrop_path:
            backdrop_path = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
        poster_path = base_data.get("poster_path", "")
        if poster_path:
            poster_path = f"https://image.tmdb.org/t/p/w1280{poster_path}"
        translations = []
        
        for lang in Language:
            lang_data = tmdb_data[lang]
            translation = MovieTranslationTable(
                movie_id=movie_id,
                language=lang.value,
                title=lang_data["title"],
                overview=lang_data["overview"],
                tagline=lang_data.get("tagline", ""),
                poster_path=poster_path,
                backdrop_path=backdrop_path,
            )
            translations.append(translation)

        # Create ratings
        ratings = []
        if omdb_data and "Ratings" in omdb_data:
            for rating_data in omdb_data["Ratings"]:
                source = RatingSource.from_omdb_source(rating_data["Source"])
                if source:
                    rating = MovieRatingTable(
                        movie_id=movie_id,
                        source=source,
                        normalized_value=self._normalize_rating(source, rating_data["Value"]),
                        raw_value=rating_data["Value"]
                    )
                    ratings.append(rating)

        # Create trailers and their translations
        trailers = []
        trailer_translations = []
        
        # Get trailer data from English response
        base_videos = tmdb_data[Language.ENGLISH_US].get("videos", {}).get("results", [])
        
        for video in base_videos:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                trailer_id = uuid.uuid4()
                trailer = MovieTrailerTable(
                    id=trailer_id,
                    movie_id=movie_id,
                    published_at=datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    official=video["official"],
                    size=video["size"],
                    type=video["type"],
                    site=video["site"]
                )
                trailers.append(trailer)
                
                # Add translations for each language
                for lang in Language:
                    # Find matching video in language-specific response
                    lang_videos = tmdb_data[lang].get("videos", {}).get("results", [])
                    matching_video = next(
                        (v for v in lang_videos if v["id"] == video["id"]), 
                        video  # Fallback to English if no translation exists
                    )
                    
                    translation = MovieTrailerTranslationTable(
                        trailer_id=trailer_id,
                        language=lang.value,
                        title=matching_video["name"],
                        key=matching_video["key"]
                    )
                    trailer_translations.append(translation)

        return movie, translations, screening, ratings, trailers, trailer_translations

    async def fetch_and_process_movies(self) -> list[tuple[MovieTable, list[MovieTranslationTable], MovieScreeningTable, list[MovieRatingTable], list[MovieTrailerTable], list[MovieTrailerTranslationTable]]]:
        """Fetch LMU movies and enrich with TMDB and OMDB data"""
        logger.info("Starting movie fetch process")
        
        lmu_movies: list[LmuMovie] = crawl_lmu_movie_data()
        for movie in lmu_movies:
            print(movie)
            
            
        processed_movies = []

        for lmu_movie in lmu_movies:
            if lmu_movie.title == "Surprise Movie":
                continue

            logger.info(f"Processing movie: {lmu_movie.title}")
            
            # Get TMDB data
            tmdb_data = self._search_tmdb_movie(lmu_movie.title, lmu_movie.year)
            if not tmdb_data:
                logger.warning(f"Could not find TMDB data for {lmu_movie.title}")
                continue

            # Get IMDB ID from TMDB data and fetch OMDB data
            imdb_id = tmdb_data[Language.ENGLISH_US]["external_ids"]["imdb_id"]
            omdb_data = self._get_omdb_data(imdb_id)
            if not omdb_data:
                logger.warning(f"Could not find OMDB data for {lmu_movie.title}")
                continue

            # Create model instances (updated to include trailers)
            movie, translations, screenings, ratings, trailers, trailer_translations = self._create_movie_model(tmdb_data, omdb_data, lmu_movie)
            processed_movies.append((movie, translations, screenings, ratings, trailers, trailer_translations))
            
            logger.info(f"Successfully processed {lmu_movie.title}")

        logger.info(f"Completed processing {len(processed_movies)} movies")
        return processed_movies 