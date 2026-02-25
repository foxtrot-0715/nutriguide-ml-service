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
            print(" [!] Ошибка декодирования JSON")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        task_id = data.get("task_id")
        # 1. Жесткая валидация task_id
        if task_id is None or not isinstance(task_id, int):
            print(f" [!] Невалидный task_id: {task_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        input_text = data.get("features", {}).get("input_data", "")
        
        # 2. Мгновенная проверка на пустые данные
        if not input_text or str(input_text).strip() == "":
            raise ValueError("Пустые входные данные для модели (требуется возврат средств)")

        print(f" [x] Начинаю обработку задачи {task_id}: {input_text}")
        
        # Имитация тяжелых вычислений
        time.sleep(3) 

        prediction = f"AI Анализ для '{input_text}': ~450 ккал, Белки: 30г, Жиры: 15г, Углеводы: 50г."

        task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
        if task:
            task.status = models.TaskStatus.COMPLETED
            task.result = prediction
            db.commit()
            print(f" [v] Задача {task_id} успешно завершена")
            
    except Exception as e:
        print(f" [!] Ошибка при обработке {task_id}: {e}")
        
        # 3. ЛОГИКА ВОЗВРАТА (Refund)
        if task_id:
            task = db.query(models.MLTask).filter(models.MLTask.id == task_id).first()
            if task:
                task.status = models.TaskStatus.FAILED
                
                balance = db.query(models.Balance).filter(models.Balance.user_id == task.user_id).first()
                if balance:
                    balance.credits += 10
                    # Фиксируем транзакцию возврата
                    refund_tx = models.Transaction(
                        user_id=task.user_id, 
                        amount=10.0, 
                        type="refund"
                    )
                    db.add(refund_tx)
                
                db.commit()
                print(f" [!] 10 кредитов возвращены пользователю (ID задачи: {task_id})")
    finally:
        db.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Даем время RabbitMQ и БД подняться
    time.sleep(5)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ml_tasks', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='ml_tasks', on_message_callback=process_task)

    print(' [*] Worker запущен и готов к работе. Ожидание задач...')
    channel.start_consuming()

if __name__ == '__main__':
    main()
