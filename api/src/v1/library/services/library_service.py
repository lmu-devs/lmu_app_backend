import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.src.v1.core.service.like_service import LikeService
from api.src.v1.core.translation_utils import apply_translation_query
from shared.src.core.exceptions import DatabaseError, NotFoundError
from shared.src.core.logging import get_main_logger
from shared.src.enums import LanguageEnum
from shared.src.tables.library.library_area_table import LibraryAreaTable
from shared.src.tables.library.library_table import (
    LibraryFilesTable,
    LibraryLikeTable,
    LibraryTable,
    LibraryTranslationTable,
)

logger = get_main_logger(__name__)


class LibraryService:
    def __init__(self, db: AsyncSession) -> None:
        """Initialize the LibraryService with a database session."""
        self.db = db
        self.like_service = LikeService(db)

    async def get_library(self, library_id: str, language: LanguageEnum = LanguageEnum.GERMAN) -> LibraryTable:
        """Retrieve a library from the database by its ID."""
        try:
            stmt = (
                select(LibraryTable)
                .options(
                    selectinload(LibraryTable.location),
                    selectinload(LibraryTable.likes),
                    selectinload(LibraryTable.files),
                )
                .where(LibraryTable.id == library_id)
            )

            # Load areas with their translations and opening hours
            stmt = stmt.options(
                selectinload(LibraryTable.areas).options(
                    selectinload(LibraryAreaTable.translations),
                    selectinload(LibraryAreaTable.opening_hours),
                )
            )

            # Apply translation logic for Library entity
            stmt = apply_translation_query(stmt, LibraryTable, LibraryTranslationTable, language)

            result = await self.db.execute(stmt)
            library = result.unique().scalar_one_or_none()

            if library is None:
                logger.error(f"Library with id {library_id} not found")
                raise NotFoundError(
                    detail=f"Library with id {library_id} not found",
                    extra={"library_id": library_id},
                )
            return library
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch library: {str(e)}")
            raise DatabaseError(detail="Failed to fetch library", extra={"original_error": str(e)}) from e

    async def get_libraries(
        self,
        library_id: Optional[str] = None,
        language: LanguageEnum = LanguageEnum.GERMAN,
    ) -> List[LibraryTable]:
        """Retrieve libraries from the database."""
        try:
            stmt = select(LibraryTable).options(
                selectinload(LibraryTable.location),
                selectinload(LibraryTable.likes),
                selectinload(LibraryTable.files),
            )

            # Load areas with their translations and opening hours
            stmt = stmt.options(
                selectinload(LibraryTable.areas).options(
                    selectinload(LibraryAreaTable.translations),
                    selectinload(LibraryAreaTable.opening_hours),
                )
            )

            # Apply translation logic for Library entity
            stmt = apply_translation_query(stmt, LibraryTable, LibraryTranslationTable, language)

            if library_id:
                stmt = stmt.where(LibraryTable.id == library_id)

            result = await self.db.execute(stmt)
            libraries = result.unique().scalars().all()

            if library_id and not libraries:
                logger.error(f"Library with id {library_id} not found")
                raise NotFoundError(
                    detail=f"Library with id {library_id} not found",
                    extra={"library_id": library_id},
                )

            return libraries

        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch libraries: {str(e)}")
            raise DatabaseError(detail="Failed to fetch libraries", extra={"original_error": str(e)}) from e

    async def toggle_like(self, library_id: str, user_id: uuid.UUID) -> bool:
        """Toggle like status for a library by user.

        Returns:
            bool: True if library is now liked, False if unliked
        """
        return await self.like_service.toggle_like(LibraryLikeTable, library_id, user_id)
