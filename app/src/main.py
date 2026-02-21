from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import pika, json, logging
from src.database.database import get_db, init_db
from src.database import models
from src.schemas import UserCreate, UserOut, PredictRequest, PredictResponse, DepositRequest
from src.auth_utils import get_password_hash

app = FastAPI(title="NutriGuide Service")
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="User exists")
    new_user = models.User(username=user_data.username, email=user_data.email, hashed_password=get_password_hash(user_data.password))
    db.add(new_user); db.commit(); db.refresh(new_user)
    db.add(models.Balance(user_id=new_user.id, credits=100)); db.commit()
    return new_user

@app.post("/auth/login")
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user: raise HTTPException(status_code=404)
    return {"id": user.id, "username": user.username}

@app.get("/users/{user_id}/balance")
def get_balance(user_id: int, db: Session = Depends(get_db)):
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    return {"credits": balance.credits if balance else 0}

@app.post("/users/{user_id}/deposit")
def deposit(user_id: int, req: DepositRequest, db: Session = Depends(get_db)):
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    if balance: balance.credits += req.amount; db.commit()
    return {"status": "ok"}

@app.post("/predict/{user_id}", response_model=PredictResponse)
def predict(user_id: int, req: PredictRequest, db: Session = Depends(get_db)):
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).first()
    if not balance or balance.credits < 10: raise HTTPException(status_code=402)
    balance.credits -= 10
    task = models.MLTask(user_id=user_id, status=models.TaskStatus.PENDING)
    db.add(task); db.commit(); db.refresh(task)
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        ch = conn.channel(); ch.queue_declare(queue='ml_tasks', durable=True)
        ch.basic_publish(exchange='', routing_key='ml_tasks', body=json.dumps({"task_id": task.id, "features": {"input_data": req.data}}))
        conn.close()
    except: pass
    return {"task_id": task.id, "status": "pending", "created_at": task.created_at}

@app.get("/users/{user_id}/tasks", response_model=List[PredictResponse])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(models.MLTask).filter(models.MLTask.user_id == user_id).order_by(desc(models.MLTask.id)).all()
    # Ручная сборка результата для стабильности
    return [
        PredictResponse(
            task_id=t.id, 
            status=str(t.status.value), 
            result=t.result, 
            created_at=t.created_at
        ) for t in tasks
    ]
