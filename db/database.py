from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine(
    "postgresql://postgres:1@localhost/api", echo=True, convert_unicode=True
)

Base = declarative_base()
Session = sessionmaker()
session = Session(bind=engine)
