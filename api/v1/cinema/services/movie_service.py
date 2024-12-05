from typing import List, Optional
import uuid
from sqlalchemy import select, case
from sqlalchemy.orm import Session, joinedload, contains_eager

from api.v1.core.translation_utils import create_translation_order_case
from shared.enums.language_enums import LanguageEnum
from shared.tables.university_table import UniversityTable, UniversityTranslationTable
from shared.tables.cinema import MovieTable, MovieScreeningTable, MovieTranslationTable, MovieTrailerTable, MovieTrailerTranslationTable
from ..schemas.movie_schema import Movie, MovieScreening

class MovieService:
    def __init__(self, db: Session):
        self.db = db
        
    def _get_movie(self, movie_id: uuid.UUID) -> Movie:
        return self.db.query(MovieTable).filter(MovieTable.id == movie_id).first()
    
    def get_movies(self, movie_id: Optional[uuid.UUID] = None) -> List[Movie]:
        if movie_id:
            return [self._get_movie(movie_id)]
        return self.db.query(MovieTable).all()
    
    def get_movie_screenings(self, language: LanguageEnum = LanguageEnum.GERMAN) -> List[MovieScreening]:
        stmt = select(MovieScreeningTable)
        
        return self.db.execute(stmt).scalars().all()
    

    
    def get_movie_screenings_query(self, language: LanguageEnum):
        
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
            create_translation_order_case(MovieTrailerTranslationTable, language)
        )

    
    def get_movie_screenings(self, language: LanguageEnum):
        query = self.get_movie_screenings_query(language)
        return self.db.execute(query).scalars().unique().all()
    