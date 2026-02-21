from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from src.database.models import GenderEnum, TaskStatus

# --- Схемы пользователя ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    gender: Optional[GenderEnum] = None
    age: Optional[int] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

# --- Схемы баланса ---
class DepositRequest(BaseModel):
    amount: int

# --- Схемы ML ---
class PredictRequest(BaseModel):
    data: str 

class PredictResponse(BaseModel):
    task_id: int
    status: TaskStatus
    result: Optional[str]
    # Добавляем для истории UI
    created_at: Optional[datetime] = None 
    cost: int = 10
    
    class Config:
        from_attributes = True
