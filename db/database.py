from typing import AsyncIterator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from settings import LOGGER

DB_USER = config('POSTGRES_USER')
DB_PASSWORD = config('POSTGRES_PASSWORD')
DB_ADDRESS = config('POSTGRES_ADDRESS')
DB_NAME = config('POSTGRES_DB')
REDIS_LIMITER = config('REDIS_LIMITER',cast=str)
REDIS_LIMITER_PORT = config('REDIS_LIMITER_PORT', cast=int)
REDIS_LIMITER_DB = config('REDIS_LIMITER_DB', cast=int)
# engine = create_async_engine(
#     f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}", echo=False, convert_unicode=True
# )
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}", echo=False, convert_unicode=True
)
engine.execution_options(stream_results=True)
redis_conn = Redis(host=REDIS_LIMITER, port=REDIS_LIMITER_PORT, db=REDIS_LIMITER_DB, decode_responses=True)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


async def init_db():
    # develop mode (not recommend)
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    LOGGER.info('init db starting ....')

# none async


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# query with async
# async def init_db():
#     async with engine.begin() as session:
#         await session.run_sync(Base.metadata.create_all)
# async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# async def get_db() -> AsyncIterator[AsyncSession]:
#     async with async_session() as db:
#         yield db
