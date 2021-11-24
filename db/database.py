from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config

DB_USER = config('POSTGRES_USER')
DB_PASSWORD = config('POSTGRES_PASSWORD')
DB_ADDRESS=config('POSTGRES_ADDRESS')
DB_NAME = config('POSTGRES_DB')

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}", echo=False, convert_unicode=True
)

Base = declarative_base()
Session_maker = sessionmaker()
session = Session_maker(bind=engine)
