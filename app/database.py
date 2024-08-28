from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy_utils import database_exists, create_database
# from local_settings import postgresql as settings


def get_engine(user, password, host, port, db):
    url = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url)
    return engine

engine = get_engine('user', 'password', 'db', '5432', 'database')
print(engine.url)


# def get_engine_from_settings():
#     keys = ['user', 'password', 'host', 'port', 'database']
#     if not all(key in keys for key in settings.keys()):
#         raise Exception('Bad Config File')
    
#     return get_engine(**settings)



def get_session():
    engine = get_engine('user', 'password', 'db', '5432', 'database')
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    return session


Base = declarative_base()

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()
        