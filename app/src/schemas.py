from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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
    status: str 
    result: Optional[str] = None
    created_at: Optional[datetime] = None 
    
    class Config:
        from_attributes = True
