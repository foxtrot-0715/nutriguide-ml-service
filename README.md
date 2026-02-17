# NutriGuide ML Service

Сервис для анализа состава продуктов питания с использованием машинного обучения.

## Текущий этап:
- [x] Спроектированы базовые доменные модели (ООП).
- [x] Настроена инфраструктура (Docker: PostgreSQL, RabbitMQ, Nginx).
- [x] Реализована интеграция с БД (SQLAlchemy 2.0).
- [x] Разработана логика биллинга и транзакций.
- [ ] Разработка REST API (в разработке).

## Как запустить инициализацию базы:
1. Поднимите контейнеры: `docker compose up -d`
2. Создайте таблицы и админа: 
   `docker compose exec app env PYTHONPATH=/app DATABASE_URL=postgresql://admin:secret_password@database:5432/nutriguide python3 -m src.init_db`

## Проверка логики:
Запустите тест биллинга (создание пользователя, списание кредитов, история):
`docker compose exec app env PYTHONPATH=/app DATABASE_URL=postgresql://admin:secret_password@database:5432/nutriguide python3 -m src.test_logic`
