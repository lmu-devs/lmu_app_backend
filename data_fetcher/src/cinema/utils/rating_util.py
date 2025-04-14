from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.enums import RatingSourceEnum

settings = get_settings()
logger = get_cinema_fetcher_logger(__name__)


class MovieRatingNormalizer:
    def __init__(self) -> None:
        pass

    def normalize_rating(self, source: RatingSourceEnum, value: str) -> float:
        """Convert various rating formats to a 0-1 scale"""
        try:
            if source == RatingSourceEnum.IMDB:
                # IMDB: "8.3/10" -> 0.83
                return float(value.split("/")[0]) / 10
            elif source == RatingSourceEnum.ROTTEN_TOMATOES:
                # Rotten Tomatoes: "98%" -> 0.98
                return float(value.rstrip("%")) / 100
            elif source == RatingSourceEnum.METACRITIC:
                # Metacritic: "88/100" -> 0.88
                return float(value.split("/")[0]) / 100
        except (ValueError, IndexError) as e:
            logger.error(f"Error normalizing rating {value} for source {source}: {e}")
            return 0.0
