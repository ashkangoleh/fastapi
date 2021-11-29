from db.database import engine, Base
from model.models import User, Order

def init_db():
    Base.metadata.create_all(bind=engine)
