from app.models.domain import User, TaskStatus, AnalysisTask

# 1. Создаем пользователя
# (Кошелек создастся автоматически внутри класса User)
me = User(user_id=1, username="Foxtrot")

print(f"--- Тест 1: Регистрация ---")
print(f"Пользователь: {me.username}, Баланс: {me.wallet.get_balance()}")

# 2. Пополняем баланс
me.wallet.top_up(1000.0)
print(f"\n--- Тест 2: Пополнение ---")
print(f"Новый баланс: {me.wallet.get_balance()}")
print(f"Количество транзакций: {len(me.wallet.history)}")

# 3. Создаем задачу на анализ
task = AnalysisTask(user_id=me.user_id, content="Куриная грудка, 200г")
print(f"\n--- Тест 3: Статусы (Enum) ---")
print(f"Статус задачи: {task.status}") # Выведет TaskStatus.CREATED
print(f"Значение статуса: {task.status.value}") # Выведет "created"

# 4. Пробуем списать деньги за анализ
price = 150.0
success = me.wallet.spend(price)

if success:
    task.status = TaskStatus.COMPLETED
    print(f"\n--- Тест 4: Списание и успех ---")
    print(f"Оплата прошла! Остаток: {me.wallet.get_balance()}")
    print(f"Статус задачи обновлен: {task.status}")
else:
    print("\n--- Тест 4: Ошибка ---")
    print("Недостаточно средств!")

# 5. Проверяем историю транзакций
print(f"\n--- Тест 5: История ---")
for tx in me.wallet.history:
    print(f"Тип: {tx.type}, Сумма: {tx.amount}, Время: {tx.timestamp}")