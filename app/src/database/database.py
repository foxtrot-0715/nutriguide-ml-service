from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.database.models import Base

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Эта функция создаст все таблицы, включая новую ml_tasks
    Base.metadata.create_all(bind=engine)
