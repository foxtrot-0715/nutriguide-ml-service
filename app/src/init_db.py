from sqlalchemy.orm import Session
from src.database.database import SessionLocal, engine
from src.database.models import Base, User, Balance, Transaction, GenderEnum, TransactionType

def init_db():
    # 1. Создаем все таблицы в базе
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 2. Проверяем, есть ли уже админ (идемпотентность)
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # Создаем Демо-Администратора
            admin = User(
                username="admin", 
                email="admin@nutriguide.com", 
                is_admin=True,
                age=35, 
                height=180.0, 
                weight=85.0, 
                gender=GenderEnum.MALE  # <--- ИСПРАВЛЕНО: Используем Enum
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            # Даем ему бесконечный (почти) баланс
            admin_balance = Balance(user_id=admin.id, credits=999999)
            db.add(admin_balance)
            
            # Фиксируем это в истории с указанием типа транзакции
            log = Transaction(
                user_id=admin.id, 
                amount=999999, 
                tx_type=TransactionType.REFILL, # <--- ИСПРАВЛЕНО: Добавлен обязательный тип
                description="Initial admin endowment"
            )
            db.add(log)
            
            print("Database initialized: Admin user created.")
        else:
            print("Database already contains data, skipping...")
            
        db.commit()
    except Exception as e:
        print(f"Initialization error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
