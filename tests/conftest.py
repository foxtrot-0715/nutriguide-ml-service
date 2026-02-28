import os
import sys
from unittest.mock import MagicMock

# ШАГ 0: Принудительная изоляция окружения
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
# Ставим заглушку для хоста RabbitMQ
os.environ["RABBITMQ_HOST"] = "localhost"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

# Добавляем путь к /app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

# Импортируем твои модули
try:
    from src import queue_utils
except ImportError:
    queue_utils = None

from src.main import app
from src.database.database import get_db
from src.database.models import Base

# Настройка SQLite
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def mock_pika_and_queue(monkeypatch):
    """
    Полностью изолируем тесты от RabbitMQ и реальной отправки сообщений.
    """
    # 1. Глушим функцию в твоем queue_utils (исправлено на send_to_queue)
    if queue_utils:
        monkeypatch.setattr("src.queue_utils.send_to_queue", lambda *args, **kwargs: print(" [MOCK] Message intercepted"))
    
    # 2. Глушим сам pika, чтобы даже если кто-то вызовет напрямую, ничего не упало
    mock_conn = MagicMock()
    monkeypatch.setattr("pika.BlockingConnection", lambda *args, **kwargs: mock_conn)
    return mock_conn

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def created_user(client):
    user_data = {"username": "testuser", "email": "test@test.com", "password": "password123"}
    client.post("/auth/register", json=user_data)
    login_res = client.post("/auth/login", json={"username": "testuser", "password": "password123"})
    return login_res.json()
