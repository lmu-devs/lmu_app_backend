import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.enums import LanguageEnum
from shared.src.tables.user_table import UserTable

from ...core.api_key import APIKey
from ...core.language import get_language
from ..models.cinema_model import Cinemas
from ..models.movie_screening_model import MovieScreenings
from ..models.movie_model import Movies
from ..services import MovieService, CinemaService, ScreeningService

router = APIRouter()

@router.get("/movies", response_model=Movies, description="Get all movies")
async def get_movie(
    id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language)
):
    movie_service = MovieService(db, language)
    movies = await movie_service.get_movies(id)
    return Movies.from_table(movies)

@router.get("/screenings", response_model=MovieScreenings, description="Get all movie screenings")
async def get_movie_screenings(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language)
):
    screening_service = ScreeningService(db, language)
    screenings = await screening_service.get_movie_screenings()
    return MovieScreenings.from_table(screenings)


@router.get("/cinemas", response_model=Cinemas, description="Get cinemas")
async def get_cinemas(
    id: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language),
):
    cinema_service = CinemaService(db, language)
    cinemas = await cinema_service.get_cinemas(id)
    return Cinemas.from_table(cinemas)
