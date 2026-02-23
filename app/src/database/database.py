import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://nutri_user:nutri_password@database:5432/nutriguide"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
