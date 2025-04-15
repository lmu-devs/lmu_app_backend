from psycopg2.errors import UniqueViolation
from sqlalchemy.orm import Session

from data_fetcher.src.cinema.services.screening_service import ScreeningService
from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.tables import (
    MovieLocationTable,
    MovieRatingTable,
    MovieScreeningTable,
    MovieTable,
    MovieTrailerTable,
    MovieTrailerTranslationTable,
    MovieTranslationTable,
)

from ..constants.cinema_constants import (
    hm_cinema,
    lmu_cinema,
    tum_cinema,
    tum_garching_cinema,
)

logger = get_cinema_fetcher_logger(__name__)


class CinemaService:
    def __init__(self, db: Session):
        self.settings = get_settings()
        self.db = db

    def add_constant_cinema_data(self):
        cinemas = [lmu_cinema, hm_cinema, tum_cinema, tum_garching_cinema]

        for cinema in cinemas:
            self.db.merge(cinema)
        self.db.commit()
        logger.info(f"Successfully added {len(cinemas)} cinemas to database")

    def clear_cinema_tables(self):
        """Clear all cinema-related tables in the correct order"""
        logger.info("Clearing movies, screenings, ratings, trailers, trailer translations and locations data...")

        self.db.query(MovieLocationTable).delete()
        self.db.query(MovieTrailerTranslationTable).delete()
        self.db.query(MovieTrailerTable).delete()
        self.db.query(MovieRatingTable).delete()
        self.db.query(MovieScreeningTable).delete()
        self.db.query(MovieTranslationTable).delete()
        self.db.query(MovieTable).delete()

        self.db.commit()
        logger.info("Successfully cleared all tables")

    async def fetch_scheduled_data(self):
        self.clear_cinema_tables()
        screening_service = ScreeningService()
        processed_movies = await screening_service.fetch_and_process_movies()

        for (
            movie,
            translations,
            screening,
            ratings,
            trailers,
            trailer_translations,
        ) in processed_movies:
            try:
                self.db.merge(movie)
                self.db.flush()

                for translation in translations:
                    self.db.merge(translation)

                self.db.merge(screening)

                for rating in ratings:
                    self.db.merge(rating)

                for trailer in trailers:
                    self.db.merge(trailer)

                for trailer_translation in trailer_translations:
                    self.db.merge(trailer_translation)

                self.db.commit()
                logger.info(
                    f"Successfully added screening {screening.cinema_id} for {movie.original_title} to database"
                )

            except Exception as e:
                self.db.rollback()
                # Check if it's a unique violation error
                if isinstance(e.__cause__, UniqueViolation):
                    logger.info(f"Movie {movie.original_title} already exists in database, skipping...")
                else:
                    logger.error(f"Error adding movie {movie.original_title} to database: {e}")
                continue
