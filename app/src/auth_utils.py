import bcrypt

def get_password_hash(password: str) -> str:
    """
    Превращает чистый пароль в хэш с использованием прямого вызова bcrypt.
    Это решает проблему совместимости passlib и новых версий bcrypt в Docker.
    """
    # Переводим строку в байты (utf-8)
    pwd_bytes = password.encode('utf-8')
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Хэшируем
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    # Возвращаем как строку для записи в базу (PostgreSQL String)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введенный пароль сохраненному хэшу.
    """
    # Переводим входные данные в байты для сравнения
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    # Проверяем
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)
