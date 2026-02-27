import pika
import json
import time
from sqlalchemy.orm import Session
from src.database.database import SessionLocal
from src.database import models

def process_task(ch, method, properties, body):
    db = SessionLocal()
    task_id = None
    try:
        try:
            data = json.loads(body)
        except Exception:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        task_id = data.get("task_id")
        if task_id is None or not isinstance(task_id, int):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        input_text = data.get("features", {}).get("input_data", "")
        
        # Рефанд при пустом вводе
        if not input_text or str(input_text).strip() == "":
            raise ValueError("Empty input")

        print(f" [x] Processing task {task_id}")
        time.sleep(3) 

        prediction = f"AI Анализ для '{input_text}': ~450 ккал, Б: 30г, Ж: 15г, У: 50г."
        task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
        if task:
            task.status = models.TaskStatus.COMPLETED
            task.result = prediction
            db.commit()
            
    except Exception as e:
        print(f" [!] Refund logic triggered for task {task_id}: {e}")
        if task_id:
            task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
            if task:
                task.status = models.TaskStatus.FAILED
                balance = db.query(models.Balance).filter(models.Balance.user_id == task.user_id).first()
                if balance:
                    balance.credits += 10
                    db.add(models.Transaction(user_id=task.user_id, amount=10.0, type="refund"))
                db.commit()
    finally:
        db.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Цикл переподключения к RabbitMQ
    while True:
        try:
            print(' [*] Попытка подключения к RabbitMQ...')
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=600))
            channel = connection.channel()
            channel.queue_declare(queue='ml_tasks', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='ml_tasks', on_message_callback=process_task)
            print(' [*] Успешно! Ожидание задач...')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print(" [!] RabbitMQ не готов. Ждем 5 секунд...")
            time.sleep(5)
        except Exception as e:
            print(f" [!] Непредвиденная ошибка: {e}. Перезапуск через 5 сек...")
            time.sleep(5)

if __name__ == '__main__':
    main()
