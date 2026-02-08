FROM python:3.10-slim

WORKDIR /app

# Копируем requirements из корня в текущую папку контейнера
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем содержимое папки app (где лежит src) внутрь /app в контейнере
COPY . .

# Команда для запуска (как модуль)
CMD ["python", "-m", "src.domain"]
