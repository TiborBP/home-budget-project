from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    initial_balance = Column(Numeric(12, 2), default=1000)
    created_at = Column(TIMESTAMP, server_default=func.now())

    categories = relationship("Category", back_populates="user")
    expenses = relationship("Expense", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="categories")
    expenses = relationship(
        "Expense",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, server_default=func.current_date())
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
