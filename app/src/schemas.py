from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Схемы пользователя ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)

# --- Схемы аналитики (Predict) ---
class PredictRequest(BaseModel):
    # Field(default="") позволяет Pydantic принять пустой запрос 
    # и передать его в main.py для логики возврата средств
    data: str = Field(default="") 

class PredictResponse(BaseModel):
    # validation_alias="id" связывает поле 'id' из БД с полем 'task_id' для фронтенда
    task_id: int = Field(validation_alias="id")
    status: str 
    result: Optional[str] = None
    created_at: Optional[datetime] = None 
    
    # populate_by_name позволяет работать и с task_id, и с id
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# --- Схемы транзакций ---
class TransactionOut(BaseModel):
    id: int
    amount: float
    type: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DepositRequest(BaseModel):
    # gt=0 гарантирует, что нельзя пополнить баланс на отрицательную сумму
    amount: float = Field(..., gt=0)
