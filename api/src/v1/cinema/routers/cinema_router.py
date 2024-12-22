import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.src.enums import LanguageEnum
from shared.src.core.database import get_db
from shared.src.tables.user_table import UserTable
from ...core.api_key import APIKey
from ...core.language import get_language
from ..pydantics.cinema_pydantic import screenings_to_pydantic, movies_to_pydantic
from ..schemas.cinema_schema import Movie, MovieScreening
from ..services.cinema_service import MovieService

router = APIRouter()

@router.get("/movies", response_model=List[Movie], description="Get all movies")
async def get_movie(
    id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language)
):
    movie_service = MovieService(db)
    movies = movie_service.get_movies(language, id)
    return movies_to_pydantic(movies)

@router.get("/screenings", response_model=List[MovieScreening], description="Get all movie screenings")
async def get_movie_screenings(
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language)
):
    movie_service = MovieService(db)
    screenings = movie_service.get_movie_screenings(language)
    return screenings_to_pydantic(screenings)