from db.database import engine, Base
from model.models import User, Order

Base.metadata.create_all(bind=engine)
