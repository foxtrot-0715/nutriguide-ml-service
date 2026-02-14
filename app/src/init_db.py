from src.database import SessionLocal, engine, Base
from src.models import User, Balance, Transaction

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
                age=35, height=180.0, weight=85.0, gender="male"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            # Даем ему бесконечный (почти) баланс
            admin_balance = Balance(user_id=admin.id, credits=999999)
            db.add(admin_balance)
            
            # Фиксируем это в истории
            log = Transaction(user_id=admin.id, amount=999999, description="Initial admin endowment")
            db.add(log)
            
            print("База инициализирована: Админ создан!")
        else:
            print("База уже содержит данные, пропускаем...")
            
        db.commit()
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
