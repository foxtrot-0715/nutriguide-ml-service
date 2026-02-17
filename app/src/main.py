from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database.database import SessionLocal, engine
from src.database.models import Base, User, Balance, Transaction, MLTask, TransactionType
from src.schemas import UserCreate, UserOut, BalanceOut, DepositRequest, PredictRequest, PredictResponse, TransactionOut

# Инициализация таблиц при старте
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriGuide ML Service API")

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. AUTH & USERS ---

@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        gender=user_data.gender,
        age=user_data.age
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Создаем стартовый баланс 0
    new_balance = Balance(user_id=new_user.id, credits=0)
    db.add(new_balance)
    db.commit()
    
    return new_user

# --- 2. BALANCE ---

@app.get("/balance/{user_id}", response_model=BalanceOut)
def get_balance(user_id: int, db: Session = Depends(get_db)):
    balance = db.query(Balance).filter(Balance.user_id == user_id).first()
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return balance

@app.post("/balance/{user_id}/deposit", response_model=BalanceOut)
def deposit(user_id: int, req: DepositRequest, db: Session = Depends(get_db)):
    balance = db.query(Balance).filter(Balance.user_id == user_id).first()
    if not balance:
        raise HTTPException(status_code=404, detail="User not found")
    
    balance.credits += req.amount
    
    # Логируем транзакцию
    new_tx = Transaction(
        user_id=user_id,
        amount=req.amount,
        tx_type=TransactionType.REFILL,
        description="Deposit via API"
    )
    db.add(new_tx)
    db.commit()
    db.refresh(balance)
    return balance

# --- 3. PREDICT (ML) ---

@app.post("/predict/{user_id}", response_model=PredictResponse)
def predict(user_id: int, req: PredictRequest, db: Session = Depends(get_db)):
    cost = 20 # Стоимость одного запроса
    balance = db.query(Balance).filter(Balance.user_id == user_id).first()
    
    if not balance or balance.credits < cost:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Списываем кредиты
    balance.credits -= cost
    
    # Создаем задачу
    new_task = MLTask(
        user_id=user_id,
        result=f"Processed: {req.data}" # Заглушка ML логики
    )
    
    # Логируем списание
    new_tx = Transaction(
        user_id=user_id,
        amount=-cost,
        tx_type=TransactionType.WITHDRAWAL,
        description="ML Prediction Charge"
    )
    
    db.add(new_task)
    db.add(new_tx)
    db.commit()
    db.refresh(new_task)
    
    return {
        "task_id": new_task.id,
        "status": new_task.status,
        "result": new_task.result
    }

# --- 4. HISTORY ---

@app.get("/history/{user_id}/transactions", response_model=List[TransactionOut])
def get_transactions(user_id: int, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()
