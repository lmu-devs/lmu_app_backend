import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.database import get_async_db
from shared.src.enums import LanguageEnum
from shared.src.tables.user_table import UserTable

from ...core.api_key import APIKey
from ...core.language import get_language
from ..pydantics.cinema_pydantic import cinemas_to_pydantic, movies_to_pydantic, screenings_to_pydantic
from ..schemas.cinema_schema import Cinema, Movie, MovieScreening
from ..services import MovieService, CinemaService, ScreeningService
router = APIRouter()

@router.get("/movies", response_model=List[Movie], description="Get all movies")
async def get_movie(
    id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language)
):
    movie_service = MovieService(db, language)
    movies = await movie_service.get_movies(id)
    return movies_to_pydantic(movies)

@router.get("/screenings", response_model=List[MovieScreening], description="Get all movie screenings")
async def get_movie_screenings(
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language)
):
    screening_service = ScreeningService(db, language)
    screenings = await screening_service.get_movie_screenings()
    return screenings_to_pydantic(screenings)


@router.get("/cinemas", response_model=List[Cinema], description="Get cinemas")
async def get_cinemas(
    id: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserTable = Depends(APIKey.verify_user_api_key_soft),
    language: LanguageEnum = Depends(get_language),
):
    cinema_service = CinemaService(db, language)
    cinemas = await cinema_service.get_cinemas(id)
    return cinemas_to_pydantic(cinemas)
