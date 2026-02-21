import enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, func, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(SQLEnum(GenderEnum), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    balance: Mapped["Balance"] = relationship("Balance", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tasks: Mapped[List["MLTask"]] = relationship("MLTask", back_populates="user")

class Balance(Base):
    __tablename__ = "balances"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    credits: Mapped[int] = mapped_column(default=100)
    user: Mapped["User"] = relationship("User", back_populates="balance")

class MLTask(Base):
    __tablename__ = "ml_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Добавляем автоматическую дату, чтобы история не была пустой
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user: Mapped["User"] = relationship("User", back_populates="tasks")
