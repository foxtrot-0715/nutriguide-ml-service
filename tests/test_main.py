import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

# 1. Форсируем локальный адрес до импорта приложения
os.environ["DATABASE_URL"] = "postgresql://nutri_user:nutri_password@127.0.0.1:5432/nutriguide"

# 2. Настройка путей
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.main import app
client = TestClient(app)

def test_full_workflow():
    unique_suffix = uuid.uuid4().hex[:6]
    test_user = {
        "username": f"pilot_{unique_suffix}",
        "email": f"pilot_{unique_suffix}@example.com",
        "password": "testpassword123"
    }

    # Регистрация
    reg_response = client.post("/auth/register", json=test_user)
    assert reg_response.status_code == 200
    
    # Логин
    login_response = client.post("/auth/login", json={
        "username": test_user["username"],
        "password": test_user["password"],
        "email": test_user["email"]
    })
    assert login_response.status_code == 200
    user_id = login_response.json()["id"]

    # Баланс
    bal_response = client.get(f"/users/{user_id}/balance")
    assert bal_response.status_code == 200
    assert bal_response.json()["credits"] >= 100
