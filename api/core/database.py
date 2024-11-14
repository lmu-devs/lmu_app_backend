import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy_utils import database_exists, create_database


Base = declarative_base()


def get_engine(user, password, host, port, db):
    url = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url)
    return engine


DB_USER = os.environ.get('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB')


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME))

def init_db():
    # Create an engine
    engine = get_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    
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
        