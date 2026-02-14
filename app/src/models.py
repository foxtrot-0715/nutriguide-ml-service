from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    gender = Column(String)
    is_admin = Column(Boolean, default=False)

    # Связь с балансом (один к одному)
    balance = relationship("Balance", back_populates="user", uselist=False)

class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    credits = Column(Integer, default=0) # Храним в целых единицах

    user = relationship("User", back_populates="balance")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)  # Положительное — пополнение, отрицательное — списание
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
