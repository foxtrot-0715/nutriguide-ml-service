from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum  # Импортируем Enum
from typing import List, Optional

# --- 1. ПРАВКА: Перечисления для статусов ---
class TaskStatus(Enum):
    CREATED = "created"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

# --- 2. ПРАВКА: История (Транзакции и Предсказания) ---
class Transaction:
    def __init__(self, amount: float, transaction_type: str):
        self.amount = amount
        self.type = transaction_type  # "top_up" или "spend"
        self.timestamp = datetime.now()

class PredictionResult:
    def __init__(self, content: str, result: str):
        self.content = content
        self.result = result
        self.timestamp = datetime.now()

# --- Логика Кошелька (добавлено ведение истории) ---
class Wallet:
    def __init__(self, initial_balance: float = 0.0):
        self.__balance = initial_balance
        self.history: List[Transaction] = []  # Список транзакций

    def top_up(self, amount: float):
        if amount > 0:
            self.__balance += amount
            self.history.append(Transaction(amount, "top_up"))

    def spend(self, amount: float) -> bool:
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            self.history.append(Transaction(amount, "spend"))
            return True
        return False

    def get_balance(self) -> float:
        return self.__balance

# --- 3. ПРАВКА: Класс Пользователя ---
class User:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.wallet = Wallet()
        self.predictions: List[PredictionResult] = [] # История предсказаний

# --- Остальное (Еда и Анализаторы) остается без изменений ---
class BaseFoodComponent(ABC):
    def __init__(self, name: str, calories: float):
        self.name = name
        self.calories = calories

class Ingredient(BaseFoodComponent):
    def __init__(self, name: str, calories: float, safety_level: str = "safe"):
        super().__init__(name, calories)
        self.safety_level = safety_level

class BaseAnalyzer(ABC):
    @abstractmethod
    def process(self, text: str):
        pass

class CalorieCounter(BaseAnalyzer):
    def process(self, text: str):
        return f"Анализ калорий для: {text}..."

class AnalysisTask:
    def __init__(self, user_id: int, content: str):
        self.user_id = user_id
        self.content = content
        # Используем наш Enum вместо строки
        self.status = TaskStatus.CREATED 
        self.created_at = datetime.now()