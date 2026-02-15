import enum
from datetime import datetime
from sqlalchemy import ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

# --- Перечисления (Enums) ---

class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class TransactionType(str, enum.Enum):
    REFILL = "refill"          # Пополнение
    WITHDRAWAL = "withdrawal"  # Списание
    BONUS = "bonus"            # Бонус

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# --- Модели данных ---

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    # Используем Enum для пола
    gender: Mapped[GenderEnum] = mapped_column(SQLEnum(GenderEnum), nullable=True)
    
    age: Mapped[int | None]
    height: Mapped[float | None]
    weight: Mapped[float | None]
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    credits: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(nullable=False)
    
    # Тип транзакции через Enum
    tx_type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    
    description: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=func.now())

class MLTask(Base):
    __tablename__ = "ml_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Статус и результат задачи
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    result: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
