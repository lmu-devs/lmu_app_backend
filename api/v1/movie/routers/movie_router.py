from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.v1.core.api_key import APIKey
from ..schemas.movie_schema import Movie, MovieScreening
from ..services.movie_service import MovieService
from shared.database import get_db
from shared.tables.user_table import UserTable

router = APIRouter()

@router.get("/movies", response_model=List[Movie], description="Get all movies")
async def get_movie(
    movie_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    movie_service = MovieService(db)
    movies = movie_service.get_movies(movie_id)
    return movies

@router.get("/movies/screenings", response_model=List[MovieScreening], description="Get all movie screenings")
async def get_movie_screenings(
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft)
):
    movie_service = MovieService(db)
    screenings = movie_service.get_movie_screenings()
    return screenings