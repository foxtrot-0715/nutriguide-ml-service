from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pika, json
from typing import List
from contextlib import asynccontextmanager

from src.database.database import get_db, init_db
from src.database import models
from src.schemas import (UserCreate, UserLogin, UserOut, PredictRequest, 
                         PredictResponse, TransactionOut, DepositRequest)
from src.auth_utils import get_password_hash, verify_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="NutriGuide Service", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="User exists")
    new_user = models.User(
        username=user_data.username, email=user_data.email, 
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    db.add(models.Balance(user_id=new_user.id, credits=100))
    db.commit()
    return new_user

@app.post("/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"id": user.id, "username": user.username}

@app.post("/predict/{user_id}")
def predict(user_id: int, req: PredictRequest, db: Session = Depends(get_db)):
    # 1. Проверка баланса
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    if not balance or balance.credits < 10:
        raise HTTPException(status_code=402, detail="Недостаточно кредитов")

    # 2. Списание
    balance.credits -= 10
    db.add(models.Transaction(user_id=user_id, amount=-10.0, type="prediction_spend"))
    db.commit()

    # 3. Проверка на пустоту (после списания!)
    if not req.data or not req.data.strip():
        # Делаем возврат
        balance.credits += 10
        db.add(models.Transaction(user_id=user_id, amount=10.0, type="refund_empty_request"))
        db.commit()
        raise HTTPException(status_code=400, detail="Пустой запрос: средства возвращены")

    # 4. Создание задачи
    task = models.MLTask(user_id=user_id, status=models.TaskStatus.PENDING)
    db.add(task); db.commit(); db.refresh(task)

    # 5. RabbitMQ
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        ch = conn.channel(); ch.queue_declare(queue='ml_tasks', durable=True)
        ch.basic_publish(
            exchange='', routing_key='ml_tasks', 
            body=json.dumps({"task_id": task.id, "features": {"input_data": req.data}})
        )
        conn.close()
    except Exception as e:
        print(f"RabbitMQ Error: {e}")
        
    return {"task_id": task.id, "status": "pending"}

@app.get("/users/{user_id}/balance")
def get_balance(user_id: int, db: Session = Depends(get_db)):
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    return {"credits": balance.credits if balance else 0}

@app.get("/users/{user_id}/transactions", response_model=List[TransactionOut])
def get_transactions(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).order_by(desc(models.Transaction.id)).all()

@app.get("/users/{user_id}/tasks", response_model=List[PredictResponse])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.MLTask).filter(models.MLTask.user_id == user_id).order_by(desc(models.MLTask.id)).all()

@app.post("/users/{user_id}/deposit")
def deposit(user_id: int, req: DepositRequest, db: Session = Depends(get_db)):
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    balance.credits += req.amount
    db.add(models.Transaction(user_id=user_id, amount=req.amount, type="deposit"))
    db.commit()
    return {"status": "ok"}
