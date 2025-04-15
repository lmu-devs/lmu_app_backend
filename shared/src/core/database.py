from typing import AsyncGenerator

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Database:
    _instance = None

    def __new__(cls, settings=None):
        if cls._instance is None:
            if settings is None:
                raise ValueError("Settings required for initial Database creation")
            cls._instance = super().__new__(cls)
            cls._instance.__init__(settings)

        return cls._instance

    def __init__(self, settings=None):
        if not hasattr(self, "engine"):
            # Sync engine and session
            self.engine = create_engine(
                f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            )
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
            )

            # Async engine and session
            self.async_engine = create_async_engine(
                f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
                echo=False,
            )
            self.AsyncSessionLocal = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )


# Keep the existing sync dependency
def get_db():
    """Get a synchronous database session dependency."""
    db = Database().SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Add the async dependency
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session dependency."""
    async with Database().AsyncSessionLocal() as session:
        async with Database().async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        try:
            yield session
        finally:
            await session.close()


def table_creation():
    engine = Database().engine
    inspector = inspect(engine)
    Base.metadata.create_all(bind=engine)
    print("Registered tables:", inspector.get_table_names())
