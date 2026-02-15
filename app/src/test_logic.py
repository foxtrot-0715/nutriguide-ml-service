from src.database.database import SessionLocal, engine
from src.database.models import User, Balance, Transaction, GenderEnum, TransactionType

def test_business_flow():
    db = SessionLocal()
    try:
        # 1. Создаем нового пользователя "Foxtrot"
        # Передаем GenderEnum.MALE вместо строки "male"
        test_user = User(
            username="foxtrot_pilot_v2", # Немного изменил имя, чтобы не было конфликта при повторном запуске
            email="pilot_v2@falcon.com",
            age=25, 
            height=185.0, 
            weight=80.0, 
            gender=GenderEnum.MALE  
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"User {test_user.username} created successfully (ID: {test_user.id})")

        # 2. Инициализируем баланс (пополнение на 100 кредитов)
        new_balance = Balance(user_id=test_user.id, credits=100)
        db.add(new_balance)
        
        # Фиксируем пополнение в истории с указанием TransactionType.REFILL
        refill_log = Transaction(
            user_id=test_user.id, 
            amount=100, 
            tx_type=TransactionType.REFILL, # Указываем тип явно
            description="Initial bonus"
        )
        db.add(refill_log)
        db.commit()
        print(f"Balance initialized: {new_balance.credits} credits")

        # 3. Имитируем запрос к ML-модели (списание 20 кредитов)
        cost = 20
        if new_balance.credits >= cost:
            new_balance.credits -= cost
            # Фиксируем списание с указанием TransactionType.WITHDRAWAL
            spend_log = Transaction(
                user_id=test_user.id, 
                amount=-cost, 
                tx_type=TransactionType.WITHDRAWAL, # Указываем тип явно
                description="ML Model computation cost"
            )
            db.add(spend_log)
            db.commit()
            print(f"Spent {cost} credits for ML-forecast. Remaining: {new_balance.credits}")

        # 4. Получаем историю транзакций
        print("\nTransaction history for user:")
        history = db.query(Transaction).filter(Transaction.user_id == test_user.id).all()
        for tx in history:
            # Выводим тип транзакции (tx_type.value), чтобы увидеть, что Enum работает
            print(f" - [{tx.created_at.strftime('%H:%M:%S')}] {tx.amount} cr ({tx.tx_type.value}): {tx.description}")

    except Exception as e:
        print(f"Test Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_business_flow()
