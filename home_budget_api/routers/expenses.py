from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import datetime
from decimal import Decimal
from typing import cast
from .. import models, schemas, database
from ..routers.auth import get_current_user
from sqlalchemy import func
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)


@router.post("/", response_model=schemas.ExpenseResponse)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    category = db.query(models.Category).filter(
        (models.Category.id == expense.category_id) &
        ((models.Category.user_id == current_user.id) | (models.Category.user_id == None))
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found or not accessible")

    current_balance: Decimal = cast(Decimal, current_user.initial_balance)
    expense_amount = Decimal(str(expense.amount))

    if current_balance - expense_amount < Decimal("0"):
        raise HTTPException(status_code=400, detail="Insufficient balance")

    current_user.initial_balance = current_balance - expense_amount  # type: ignore

    db_expense = models.Expense(
        description=expense.description,
        amount=expense.amount,
        date=expense.date,
        category_id=category.id,
        user_id=current_user.id
    )
    db.add(db_expense)
    db.add(current_user)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("/", response_model=List[schemas.ExpenseResponse])
def list_expenses(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    start_date: Optional[datetime.date] = Query(None, description="Start date"),
    end_date: Optional[datetime.date] = Query(None, description="End date")
):
    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

    if category_id:
        query = query.filter(models.Expense.category_id == category_id)
    if min_amount:
        query = query.filter(models.Expense.amount >= min_amount)
    if max_amount:
        query = query.filter(models.Expense.amount <= max_amount)
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    return query.all()


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    current_balance: Decimal = cast(Decimal, current_user.initial_balance)
    refund_amount = Decimal(str(expense.amount))
    current_user.initial_balance = current_balance + refund_amount  # type: ignore

    db.delete(expense)
    db.add(current_user)
    db.commit()
    return {"detail": "Expense deleted and amount refunded"}












# ---------------- EXPENSES OVERVIEW ----------------
@router.get("/summary", response_model=schemas.SummaryResponse)
def get_budget_summary(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns a summary of the user's budget:
    - Total spent
    - Remaining balance
    - Spending per category
    - Spending last month, last quarter, last year
    """
    from decimal import Decimal
    from typing import cast
    from sqlalchemy import func

    today = date.today()

    one_month_ago = today - relativedelta(months=1)
    three_months_ago = today - relativedelta(months=3)
    one_year_ago = today - relativedelta(years=1)

    total_spent = db.query(func.coalesce(func.sum(models.Expense.amount), 0)) \
        .filter(models.Expense.user_id == current_user.id).scalar()
    total_spent = float(total_spent)

    current_balance: Decimal = cast(Decimal, current_user.initial_balance)
    remaining_balance = float(current_balance)

    spending_by_category = (
        db.query(
            models.Category.name,
            func.coalesce(func.sum(models.Expense.amount), 0).label("total")
        )
        .join(models.Expense, models.Category.id == models.Expense.category_id)
        .filter(models.Expense.user_id == current_user.id)
        .group_by(models.Category.name)
        .all()
    )

    category_summaries = [
        schemas.CategorySummary(category=name, total=float(total))
        for name, total in spending_by_category
    ]

    def spending_since(start_date: date) -> float:
        return float(
            db.query(func.coalesce(func.sum(models.Expense.amount), 0))
            .filter(
                models.Expense.user_id == current_user.id,
                models.Expense.date >= start_date
            )
            .scalar()
        )

    spent_last_month = spending_since(one_month_ago)
    spent_last_quarter = spending_since(three_months_ago)
    spent_last_year = spending_since(one_year_ago)

    return schemas.SummaryResponse(
        total_spent=total_spent,
        remaining_balance=remaining_balance,
        by_category=category_summaries,
        spent_last_month=spent_last_month,
        spent_last_quarter=spent_last_quarter,
        spent_last_year=spent_last_year
    )