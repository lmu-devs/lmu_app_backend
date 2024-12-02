from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from shared.tables.movie_table import MovieTable, MovieScreeningTable
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
    
    def get_movie_screenings(self) -> List[MovieScreening]:
        return self.db.query(MovieScreeningTable).all()
    