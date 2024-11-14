from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Database:
    _instance = None

    def __new__(cls, settings=None):
        if cls._instance is None:
            if settings is None:
                raise ValueError("Settings required for initial Database creation")
            cls._instance = super().__new__(cls)
            cls._instance.__init__(settings)
            
            # Create all tables when database is first initialized
            Base.metadata.create_all(bind=cls._instance.engine)
            
        return cls._instance

    def __init__(self, settings=None):
        if not hasattr(self, 'engine'):
            self.engine = create_engine(
                f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
            )
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
            )

def get_db():
    """Get a database session dependency."""
    db = Database().SessionLocal()
    try:
        yield db
    finally:
        db.close()