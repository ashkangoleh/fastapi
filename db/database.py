from typing import AsyncIterator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DB_USER = config('POSTGRES_USER')
DB_PASSWORD = config('POSTGRES_PASSWORD')
DB_ADDRESS = config('POSTGRES_ADDRESS')
DB_NAME = config('POSTGRES_DB')

# engine = create_async_engine(
#     f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}", echo=False, convert_unicode=True
# )
engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}", echo=False, convert_unicode=True
)
engine.execution_options(stream_results=True)
redis_conn = Redis(host='localhost', port=6379, db=1, decode_responses=True)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print(SessionLocal())

async def init_db():
    Base.metadata.create_all(bind=engine)

# none async
def get_db():
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
