from abc import ABC, abstractmethod
from datetime import datetime

# 1. Инкапсуляция: Управление финансами пользователя
class Wallet:
    def __init__(self, initial_balance: float = 0.0):
        self.__balance = initial_balance

    def top_up(self, amount: float):
        if amount > 0:
            self.__balance += amount

    def spend(self, amount: float) -> bool:
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return True
        return False

    def get_balance(self) -> float:
        return self.__balance

# 2. Наследование и Абстракция: Продукты
class BaseFoodComponent(ABC):
    def __init__(self, name: str, calories: float):
        self.name = name
        self.calories = calories

class Ingredient(BaseFoodComponent):
    """Ингредиент наследует имя и калории, добавляя уровень опасности"""
    def __init__(self, name: str, calories: float, safety_level: str = "safe"):
        super().__init__(name, calories) # Передаем данные в родительский класс
        self.safety_level = safety_level

# 3. Полиморфизм: Анализаторы
class BaseAnalyzer(ABC):
    @abstractmethod
    def process(self, text: str):
        pass
    
class CalorieCounter(BaseAnalyzer):
    def process(self, text: str):
        return f"Анализ калорий для: {text}..."

class ToxicityScanner(BaseAnalyzer):
    def process(self, text: str):
        return f"Поиск вредных добавок в: {text}..."

# 4. Основная сущность Задачи
class AnalysisTask:
    def __init__(self, user_id: int, content: str):
        self.user_id = user_id
        self.content = content
        self.status = "created"
        self.created_at = datetime.now()