from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config

DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_ADDRESS=config('DB_ADDRESS')
DB_NAME = config('DB_NAME')

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}", echo=True, convert_unicode=True
)

Base = declarative_base()
Session = sessionmaker()
session = Session(bind=engine)
