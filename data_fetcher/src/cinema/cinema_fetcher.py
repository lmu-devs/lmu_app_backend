import asyncio
import schedule

from sqlalchemy.orm import Session
from psycopg2.errors import UniqueViolation

from shared.src.tables import MovieTable, MovieTranslationTable, MovieScreeningTable, MovieRatingTable, MovieTrailerTable, MovieTrailerTranslationTable, MovieLocationTable
from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.core.database import get_db

from ..state import running_movie
from .services.cinema_service import CinemaService
from .services.screening_service import ScreeningService

logger = get_cinema_fetcher_logger(__name__)


def add_constant_cinema_data(db: Session):
    cinema_service = CinemaService()
    cinemas = cinema_service.get_all_cinema_tables()
    for cinema in cinemas:
        db.merge(cinema)
    db.commit()
    logger.info(f"Successfully added {len(cinemas)} cinemas to database")

def clear_cinema_tables(db: Session):
    """Clear all cinema-related tables in the correct order"""
    logger.info("Clearing movies, screenings, ratings, trailers, trailer translations and locations data...")
    
    db.query(MovieLocationTable).delete()
    db.query(MovieTrailerTranslationTable).delete()
    db.query(MovieTrailerTable).delete()
    db.query(MovieRatingTable).delete()
    db.query(MovieScreeningTable).delete()
    db.query(MovieTranslationTable).delete()
    db.query(MovieTable).delete()
    
    db.commit()
    logger.info("Successfully cleared all tables")



async def fetch_scheduled_data(db: Session):
    clear_cinema_tables(db)
    screening_service = ScreeningService()
    processed_movies = await screening_service.fetch_and_process_movies()
    
    for movie, translations, screening, ratings, trailers, trailer_translations in processed_movies:
        try:
            db.merge(movie)
            db.flush()
            
            for translation in translations:
                db.merge(translation)
            
            db.merge(screening)
            
            for rating in ratings:
                db.merge(rating)
            
            for trailer in trailers:
                db.merge(trailer)
            
            for trailer_translation in trailer_translations:
                db.merge(trailer_translation)
            
            db.commit()
            logger.info(f"Successfully added screening {screening.cinema_id} for {movie.original_title} to database")
            
        except Exception as e:
            db.rollback()
            # Check if it's a unique violation error
            if isinstance(e.__cause__, UniqueViolation):
                logger.info(f"Movie {movie.original_title} already exists in database, skipping...")
            else:
                logger.error(f"Error adding movie {movie.original_title} to database: {e}")
            continue


async def create_movie_fetcher():
    logger.info("================================================")
    logger.info(f"Setting up {__name__}...")
    db = next(get_db())
    

    add_constant_cinema_data(db)
    await fetch_scheduled_data(db)
    
    async def scheduled_task():
        await fetch_scheduled_data(db)
    
    schedule.every().monday.at("08:08").do(scheduled_task)
    
    logger.info(f"Entering {__name__} loop...")
    while running_movie:
        schedule.run_pending()
        await asyncio.sleep(60)
    
    logger.info(f"Exiting {__name__} loop...")
    logger.info("================================================\n")

