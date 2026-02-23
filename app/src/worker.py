import pika
import json
import time
from sqlalchemy.orm import Session
from src.database.database import SessionLocal
from src.database import models

def process_task(ch, method, properties, body):
    data = json.loads(body)
    task_id = data.get("task_id")
    input_text = data.get("features", {}).get("input_data", "")

    print(f" [x] Начинаю обработку задачи {task_id}: {input_text}")
    
    # Имитация работы нейросети
    time.sleep(3) 
    prediction = f"AI Анализ для '{input_text}': ~450 ккал, Белки: 30г, Жиры: 15г, Углеводы: 50г. Рекомендация: Отличный выбор!"

    # Обновляем статус в базе
    db = SessionLocal()
    try:
        task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
        if task:
            task.status = models.TaskStatus.COMPLETED
            task.result = prediction
            db.commit()
            print(f" [v] Задача {task_id} завершена")
    except Exception as e:
        print(f" [!] Ошибка БД: {e}")
    finally:
        db.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Ждем RabbitMQ, если он еще не запустился
    time.sleep(5)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ml_tasks', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='ml_tasks', on_message_callback=process_task)

    print(' [*] Worker запущен. Ожидание задач...')
    channel.start_consuming()

if __name__ == '__main__':
    main()
