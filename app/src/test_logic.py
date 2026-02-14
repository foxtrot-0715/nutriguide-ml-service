from src.database import SessionLocal
from src.models import User, Balance, Transaction

def test_business_flow():
    db = SessionLocal()
    try:
        # 1. Создаем нового пользователя "Foxtrot"
        test_user = User(
            username="foxtrot_pilot", 
            email="pilot@falcon.com",
            age=25, height=185.0, weight=80.0, gender="male"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Пользователь {test_user.username} создан (ID: {test_user.id})")

        # 2. Инициализируем баланс (пополнение на 100 кредитов)
        new_balance = Balance(user_id=test_user.id, credits=100)
        db.add(new_balance)
        
        # Фиксируем пополнение в истории
        refill_log = Transaction(user_id=test_user.id, amount=100, description="Начальный бонус")
        db.add(refill_log)
        db.commit()
        print(f"Баланс пополнен: {new_balance.credits} кредитов")

        # 3. Имитируем запрос к ML-модели (списание 20 кредитов)
        cost = 20
        if new_balance.credits >= cost:
            new_balance.credits -= cost
            spend_log = Transaction(user_id=test_user.id, amount=-cost, description="Расчет рациона (ML Model)")
            db.add(spend_log)
            db.commit()
            print(f"Списано {cost} кредитов за ML-прогноз. Остаток: {new_balance.credits}")

        # 4. Получаем историю транзакций
        print("\nИстория транзакций для Foxtrot:")
        history = db.query(Transaction).filter(Transaction.user_id == test_user.id).all()
        for tx in history:
            print(f" - [{tx.created_at.strftime('%H:%M:%S')}] {tx.amount} cr: {tx.description}")

    except Exception as e:
        print(f"Ошибка теста: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_business_flow()
