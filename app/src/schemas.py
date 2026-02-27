from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from src.database.models import GenderEnum, TransactionType, TaskStatus

# Схемы пользователя
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str # В реальном проекте хешируем
    gender: Optional[GenderEnum] = None
    age: Optional[int] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    gender: Optional[GenderEnum]
    class Config:
        from_attributes = True

# Схемы баланса
class BalanceOut(BaseModel):
    credits: int
    updated_at: datetime
    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    amount: int

# Схемы ML
class PredictRequest(BaseModel):
    data: str # Здесь могут быть параметры для модели

class PredictResponse(BaseModel):
    task_id: int
    status: TaskStatus
    result: Optional[str]

class TransactionOut(BaseModel):
    id: int
    amount: int
    tx_type: TransactionType
    description: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True
