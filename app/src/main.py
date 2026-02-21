from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import pika
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.database.database import get_db, init_db
from src.database import models
# Импортируем схемы напрямую
from src.schemas import (
    UserCreate, 
    UserOut, 
    PredictRequest, 
    PredictResponse, 
    DepositRequest
)
from src.auth_utils import get_password_hash

# Инициализация БД
try:
    init_db()
    logger.info("--- СИСТЕМА НУТРИГИД ЗАПУЩЕНА И БД ПОДКЛЮЧЕНА ---")
except Exception as e:
    logger.error(f"--- ОШИБКА ИНИЦИАЛИЗАЦИИ БД: {e} ---")

app = FastAPI(title="NutriGuide ML Service Full API")

# --- Настройка фронтенда (WebUI) ---
# Подключаем папку со статикой (css, js) и шаблонами (html)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# --- 0. UI Эндпоинт (Главная страница) ---
@app.get("/", tags=["UI"])
def index(request: Request):
    """Отдает главную страницу нашего веб-интерфейса"""
    return templates.TemplateResponse("index.html", {"request": request})

# --- 1. Системные эндпоинты ---
@app.get("/health", tags=["System"])
def health():
    return {"status": "online", "message": "Ready to count calories!"}

# --- 2. Авторизация и пользователи ---
@app.post("/auth/register", response_model=UserOut, tags=["Auth"])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.username == user_data.username) | 
        (models.User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = get_password_hash(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        gender=user_data.gender,
        age=user_data.age
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Создаем стартовый баланс
    db.add(models.Balance(user_id=new_user.id, credits=100))
    db.commit()
    return new_user

# --- 3. Экономика ---
@app.get("/users/{user_id}/balance", tags=["Economy"])
def get_balance(user_id: int, db: Session = Depends(get_db)):
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return {"user_id": user_id, "credits": balance.credits}

@app.post("/users/{user_id}/deposit", tags=["Economy"])
def deposit_money(user_id: int, req: DepositRequest, db: Session = Depends(get_db)):
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    if not balance:
        raise HTTPException(status_code=404, detail="Balance record not found")
    
    balance.credits += req.amount
    db.commit()
    logger.info(f"Баланс юзера {user_id} пополнен на {req.amount}")
    return {"message": "Success", "new_balance": balance.credits}

# --- 4. ML Engine (Задачи) ---
@app.post("/predict/{user_id}", response_model=PredictResponse, tags=["ML Engine"])
def predict(user_id: int, req: PredictRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка экономики
    PREDICT_COST = 10
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    
    if not balance or balance.credits < PREDICT_COST:
        raise HTTPException(
            status_code=402, 
            detail=f"Insufficient credits. Need {PREDICT_COST}, you have {balance.credits if balance else 0}"
        )

    # Списание и создание задачи
    balance.credits -= PREDICT_COST
    new_task = models.MLTask(user_id=user_id, status=models.TaskStatus.PENDING)
    db.add(new_task)
    
    try:
        db.commit()
        db.refresh(new_task)

        # Отправка в очередь RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='ml_tasks', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='ml_tasks',
            body=json.dumps({"task_id": new_task.id, "features": {"input_data": req.data}}),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        
        return PredictResponse(task_id=new_task.id, status=new_task.status, result=new_task.result)
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail="Message broker error. Credits preserved.")

@app.get("/tasks/{task_id}", response_model=PredictResponse, tags=["ML Engine"])
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return PredictResponse(task_id=task.id, status=task.status, result=task.result)

@app.get("/users/{user_id}/tasks", response_model=List[PredictResponse], tags=["ML Engine"])
def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(models.MLTask).filter(models.MLTask.user_id == user_id).all()
    return [
        PredictResponse(
            task_id=t.id, 
            status=t.status, 
            result=t.result
        ) for t in tasks
    ]
