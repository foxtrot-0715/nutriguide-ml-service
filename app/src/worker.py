import pika
import json
import time
import joblib
import os
import sys

# 1. Настройка путей
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.database.database import SessionLocal
from src.database import models

# 2. Загрузка модели (сделаем это до подключения к RabbitMQ)
MODEL_PATH = os.path.join(parent_dir, 'models', 'food_model.joblib')
try:
    model = joblib.load(MODEL_PATH)
    print(f"🚀 [ML] Модель загружена!")
except Exception as e:
    model = None
    print(f"❌ [ML] Ошибка модели: {e}")

def process_task(ch, method, properties, body):
    print(f"📥 [ВОРКЕР] Получено сообщение из RabbitMQ!") # ЭТОТ ПРИНТ ВАЖЕН
    db = SessionLocal()
    task_id = None
    try:
        data = json.loads(body)
        task_id = data.get("task_id")
        input_text = data.get("features", {}).get("input_data", "")
        print(f"🔎 [РАБОТА] Задача #{task_id}: {input_text}")

        if model and input_text:
            res = model.predict([str(input_text).lower()])[0]
            p, f, c, kcal = round(res[0], 1), round(res[1], 1), round(res[2], 1), int(res[3])
            result_text = (
                f"✅ Результат ML-анализа для '{input_text}':\n"
                f"🥩 Б: {p}г | 🧀 Ж: {f}г | 🌾 У: {c}г\n"
                f"🔥 Калории: {kcal} ккал"
            )
        else:
            result_text = "⚠️ Ошибка модели"

        task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
        if task:
            task.status = models.TaskStatus.COMPLETED
            task.result = result_text
            db.commit()
            print(f"✨ [ГОТОВО] Задача #{task_id} сохранена.")

    except Exception as e:
        print(f"🔥 [ОШИБКА]: {e}")
        # Здесь логика рефанда (оставь свою текущую)
    finally:
        db.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Внутри Docker используем ТОЛЬКО 'rabbitmq'
    host = 'rabbitmq'
    print(f" [*] Старт воркера. Хост: {host}")
    
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, heartbeat=600)
            )
            channel = connection.channel()
            # Убедись, что параметры очереди (durable) совпадают с FastAPI!
            channel.queue_declare(queue='ml_tasks', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='ml_tasks', on_message_callback=process_task)
            
            print(f' [*] УСПЕХ! Слушаю очередь [ml_tasks]...')
            channel.start_consuming()
        except Exception as e:
            print(f" [!] Ошибка RabbitMQ: {e}. Рестарт через 5 сек...")
            time.sleep(5)

if __name__ == "__main__":
    main()
