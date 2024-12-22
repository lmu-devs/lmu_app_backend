from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, contains_eager

from shared.src.enums import LanguageEnum
from shared.src.tables import UniversityTable, UniversityTranslationTable, MovieTable, MovieScreeningTable, MovieTranslationTable, MovieTrailerTable, MovieTrailerTranslationTable, CinemaTable, CinemaTranslationTable
from ...core.translation_utils import create_translation_order_case
from ..schemas.cinema_schema import Movie, MovieScreening

class MovieService:
    def __init__(self, db: Session):
        self.db = db
        
    def _get_movie(self, movie_id: uuid.UUID) -> Movie:
        return self.db.query(MovieTable).filter(MovieTable.id == movie_id).first()
    
    def get_movies(self, language: LanguageEnum, movie_id: Optional[uuid.UUID] = None) -> List[Movie]:
        stmt = self._get_movies_query(language, movie_id)
        
        return self.db.execute(stmt).scalars().unique().all()
    
    def _get_movies_query(self, language: LanguageEnum, movie_id: Optional[uuid.UUID] = None):
        query = (select(MovieTable)
        .join(MovieTable.translations)
        .options(contains_eager(MovieTable.translations))
        
        # Join and load trailers with translations
        .outerjoin(MovieTable.trailers)
        .outerjoin(MovieTrailerTable.translations)
        .options(
            contains_eager(MovieTable.trailers)
            .contains_eager(MovieTrailerTable.translations)
        )
        )
        
        if movie_id:
            query = query.filter(MovieTable.id == movie_id)
        
        return query.order_by(
            create_translation_order_case(MovieTranslationTable, language),
            create_translation_order_case(MovieTrailerTranslationTable, language)
        )
        
        
    def get_movie_screenings(self, language: LanguageEnum):
        query = self._get_movie_screenings_query(language)
        return self.db.execute(query).scalars().unique().all()
    
    def _get_movie_screenings_query(self, language: LanguageEnum):
        
        query =  (select(MovieScreeningTable)
        # Join and load movie with its translations
        .join(MovieScreeningTable.movie)
        .outerjoin(MovieTable.translations)
        .options(contains_eager(MovieScreeningTable.movie)
                .contains_eager(MovieTable.translations))
        
        # Join and load university with its translations
        .join(MovieScreeningTable.university)
        .outerjoin(UniversityTable.translations)
        .options(contains_eager(MovieScreeningTable.university)
                .contains_eager(UniversityTable.translations))
        
        # Join and load cinema with its translations
        .join(MovieScreeningTable.cinema)
        .outerjoin(CinemaTable.translations)
        .options(contains_eager(MovieScreeningTable.cinema)
                .contains_eager(CinemaTable.translations))
        
        # Load location
        .options(joinedload(MovieScreeningTable.location))
        
        # Join and load trailers with translations
        .outerjoin(MovieTable.trailers)
        .outerjoin(MovieTrailerTable.translations)
        .options(
            contains_eager(MovieScreeningTable.movie)
            .contains_eager(MovieTable.trailers)
            .contains_eager(MovieTrailerTable.translations)
        )
        
        )
        # Order by screening date and translations
        return query.order_by(
            MovieScreeningTable.date,
            create_translation_order_case(MovieTranslationTable, language),
            create_translation_order_case(UniversityTranslationTable, language),
            create_translation_order_case(MovieTrailerTranslationTable, language),
            create_translation_order_case(CinemaTranslationTable, language)
        )

    

    