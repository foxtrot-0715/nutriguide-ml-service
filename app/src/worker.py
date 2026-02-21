import time
import json
import pika
from sqlalchemy.orm import Session
from src.database.database import SessionLocal
# Импортируем строго то, что есть в твоем models.py
from src.database.models import MLTask, TaskStatus 

def process_ml_task(task_id: str, features: dict):
    """Логика обработки задачи ML"""
    print(f" [-->] Воркер принял задачу ID: {task_id}", flush=True)
    
    db: Session = SessionLocal()
    try:
        # Поиск задачи в БД (SQLAlchemy 2.0 style)
        task = db.query(MLTask).filter(MLTask.id == int(task_id)).first()
        
        if task:
            # 1. Меняем статус на "в процессе"
            task.status = TaskStatus.PROCESSING
            db.commit()

            # 2. Имитация работы модели (5 секунд "думаем")
            time.sleep(5) 
            mock_result = f"Prediction for {features.get('input_data', 'none')}: OK (Health Score: 85)"

            # 3. Сохраняем результат и статус
            task.result = mock_result
            task.status = TaskStatus.COMPLETED
            db.commit()
            print(f" [ v ] Задача {task_id} завершена успешно.", flush=True)
        else:
            print(f" [ x ] Задача с ID {task_id} не найдена в базе!", flush=True)

    except Exception as e:
        print(f" [ x ] Ошибка воркера: {e}", flush=True)
        # Если что-то пошло не так, пытаемся пометить задачу как проваленную
        try:
            task = db.query(MLTask).filter(MLTask.id == int(task_id)).first()
            if task:
                task.status = TaskStatus.FAILED
                db.commit()
        except:
            pass
    finally:
        db.close()

def callback(ch, method, properties, body):
    """Обработчик сообщений из очереди"""
    try:
        data = json.loads(body)
        task_id = data.get("task_id")
        features = data.get("features", {})
        
        process_ml_task(task_id, features)
        
        # Подтверждаем RabbitMQ, что сообщение обработано
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] Ошибка в callback: {e}", flush=True)

def main():
    print(" [*] Воркер ожидает запуска RabbitMQ...", flush=True)
    
    # Цикл ожидания доступности RabbitMQ
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', heartbeat=600)
            )
            break
        except Exception:
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue='ml_tasks', durable=True)
    
    # Не брать больше одной задачи за раз
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='ml_tasks', on_message_callback=callback)

    print(" [*] Воркер запущен и готов к работе. Для выхода нажмите CTRL+C", flush=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
