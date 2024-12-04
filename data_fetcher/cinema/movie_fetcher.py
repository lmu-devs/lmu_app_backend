import time

import schedule
from sqlalchemy.orm import Session

from shared.core.logging import get_movie_fetcher_logger
from shared.database import get_db
from data_fetcher.state import running_movie
from .services.movie_service import MovieService

logger = get_movie_fetcher_logger(__name__)




async def fetch_scheduled_data(db: Session):
    lmu_movie_service = MovieService()
    processed_movies = await lmu_movie_service.fetch_and_process_movies()
    
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
            logger.info(f"Successfully added movie {movie.original_title} to database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding movie {movie.original_title} to database: {e}")
            continue


async def create_movie_fetcher():
    
    logger.info("Setting up schedule...")
    db = next(get_db())
    
    # Initial fetch
    await fetch_scheduled_data(db)
    
    schedule.every().day.at("08:08").do(lambda: fetch_scheduled_data(db))
    
    logger.info("Entering data_fetcher loop...")
    while running_movie:
        schedule.run_pending()
        time.sleep(10)
    
    logger.info("Exiting main loop...")


