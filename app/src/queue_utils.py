import pika
import json
import os

# Берем настройки из окружения или ставим дефолт
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "ml_tasks"

def send_to_queue(message_data: dict):
    """Отправляет JSON-сообщение в очередь RabbitMQ"""
    # 1. Устанавливаем соединение
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    # 2. Объявляем очередь (на случай, если она еще не создана)
    # durable=True значит, что очередь не пропадет при перезагрузке кролика
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # 3. Публикуем сообщение
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(message_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Делает сообщение "стойким" (сохраняется на диск)
        )
    )
    
    connection.close()
    print(f" [x] Отправлено в очередь: {message_data['task_id']}")
