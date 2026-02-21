from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from src.database.models import GenderEnum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    amount: int

class PredictRequest(BaseModel):
    data: str 

class PredictResponse(BaseModel):
    task_id: int
    status: str # Используем str вместо Enum, чтобы избежать ошибок валидации
    result: Optional[str] = None
    created_at: Optional[datetime] = None 
    cost: int = 10
    
    class Config:
        from_attributes = True
