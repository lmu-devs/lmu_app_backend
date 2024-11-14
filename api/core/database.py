from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy_utils import database_exists, create_database
from api.core.settings import get_settings

settings = get_settings()


Base = declarative_base()

def get_database_url() -> str:
    return f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'

def get_engine():
    url = get_database_url()
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url)
    return engine



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def init_db():
    # Create an engine
    engine = get_engine()
    
    # Create all Tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    session = SessionLocal()
    
    return session



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        