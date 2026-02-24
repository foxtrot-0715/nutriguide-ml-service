import os
import sys
import pytest
from fastapi.testclient import TestClient

# Конфигурация путей и окружения
os.environ["DATABASE_URL"] = "postgresql://nutri_user:nutri_password@127.0.0.1:5432/nutriguide"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.main import app

# --- ФИКСТУРЫ ---

@pytest.fixture
def client():
    """Фикстура для создания тестового клиента FastAPI"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user_data():
    """Генерация уникальных данных пользователя"""
    import uuid
    uid = uuid.uuid4().hex[:6]
    return {
        "username": f"user_{uid}",
        "email": f"user_{uid}@example.com",
        "password": "secret_password_123"
    }

@pytest.fixture
def registered_user(client, test_user_data):
    """Фикстура, которая сразу регистрирует пользователя и возвращает его данные"""
    client.post("/auth/register", json=test_user_data)
    return test_user_data

# --- ПОЗИТИВНЫЕ ТЕСТЫ ---

def test_register_success(client, test_user_data):
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    assert response.json()["username"] == test_user_data["username"]

def test_login_success(client, registered_user):
    response = client.post("/auth/login", json=registered_user)
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_balance(client, registered_user):
    # Сначала логинимся, чтобы получить ID
    login_res = client.post("/auth/login", json=registered_user)
    user_id = login_res.json()["id"]
    
    response = client.get(f"/users/{user_id}/balance")
    assert response.status_code == 200
    assert "credits" in response.json()

# --- НЕГАТИВНЫЕ ТЕСТЫ ---

def test_register_duplicate_username(client, registered_user):
    """Проверка: нельзя зарегистрировать того же юзера дважды"""
    response = client.post("/auth/register", json=registered_user)
    # Обычно 400 или 409, в зависимости от твоей логики в main.py
    assert response.status_code != 200 

def test_login_wrong_password(client, registered_user):
    """Проверка: вход с неверным паролем"""
    wrong_data = registered_user.copy()
    wrong_data["password"] = "wrong_pass"
    response = client.post("/auth/login", json=wrong_data)
    assert response.status_code == 401 # Unauthorized

def test_get_balance_non_existent_user(client):
    """Проверка: баланс несуществующего юзера"""
    response = client.get("/users/999999/balance")
    assert response.status_code == 404
