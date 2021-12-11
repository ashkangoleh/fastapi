from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config
from redis import Redis

DB_USER = config('POSTGRES_USER')
DB_PASSWORD = config('POSTGRES_PASSWORD')
DB_ADDRESS = config('POSTGRES_ADDRESS')
DB_NAME = config('POSTGRES_DB')

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}", echo=False, convert_unicode=True
)
engine.execution_options(stream_results=True)
redis_conn = Redis(host='localhost', port=6379, db=1, decode_responses=True)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
