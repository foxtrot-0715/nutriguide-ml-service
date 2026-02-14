import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Получаем URL из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем движок
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий для работы с транзакциями
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass
