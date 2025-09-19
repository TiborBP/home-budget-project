import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

# ---------- AUTH ----------
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    initial_balance: float

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class BalanceUpdate(BaseModel):
    amount: float


# ---------- CATEGORY ----------
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# ---------- EXPENSE ----------
class ExpenseBase(BaseModel):
    description: str
    amount: float
    date: Optional[datetime.date] = Field(default_factory=datetime.date.today)
    category_id: int

class ExpenseCreate(ExpenseBase):
    pass

class CategoryNested(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: float
    date: datetime.date
    category: CategoryNested

    class Config:
        from_attributes = True

# ---------- SUMMARY (EXPENSES) ----------
class CategorySummary(BaseModel):
    category: str
    total: float

class SummaryResponse(BaseModel):
    total_spent: float
    remaining_balance: float
    by_category: List[CategorySummary]
    spent_last_month: float
    spent_last_quarter: float
    spent_last_year: float

