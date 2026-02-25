import pika, json, time
from src.database.database import SessionLocal
from src.database import models

def process_task(ch, method, properties, body):
    db = SessionLocal()
    task_id = None
    try:
        # 1. ГЛУБОКАЯ ВАЛИДАЦИЯ BODY
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            print(" [!] Ошибка: Body не является валидным JSON")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        task_id = data.get("task_id")
        features = data.get("features", {})
        input_text = features.get("input_data", "") if isinstance(features, dict) else ""

        if not isinstance(task_id, int):
            print(f" [!] Ошибка: task_id отсутствует или не число: {task_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # 2. ПРОВЕРКА ДАННЫХ ДЛЯ МОДЕЛИ
        if not input_text or str(input_text).strip() == "":
            raise ValueError("Empty input data - refund required")

        print(f" [x] Processing task {task_id}...")
        time.sleep(3) # Имитация работы
        
        prediction = f"AI Анализ для '{input_text}': ~450 ккал, Белки: 30г, Жиры: 15г, Углеводы: 50г."

        task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
        if task:
            task.status = models.TaskStatus.COMPLETED
            task.result = prediction
            db.commit()
            
    except Exception as e:
        print(f" [!] Error processing task {task_id}: {e}")
        # 3. ЛОГИКА ВОЗВРАТА (REFUND)
        if task_id:
            task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
            if task and task.status != models.TaskStatus.COMPLETED:
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
    time.sleep(5)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ml_tasks', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='ml_tasks', on_message_callback=process_task)
    print(' [*] Worker is running...')
    channel.start_consuming()

if __name__ == '__main__':
    main()
