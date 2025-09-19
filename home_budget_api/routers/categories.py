from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


# ---------------- VIEW CATEGORIES ----------------
@router.get("/", response_model=list[schemas.CategoryResponse])
def list_categories(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    categories = db.query(models.Category).filter(
        (models.Category.user_id == current_user.id) | (models.Category.user_id == None)
    ).all()
    return categories


# ---------------- ADD CATEGORIES ----------------
@router.post("/", response_model=schemas.CategoryResponse)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_category = models.Category(name=category.name, user_id=current_user.id) # Can create multiple categories of same name, maybe should restrict to unique name for each category?
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# ---------------- REMOVE CATEGORIES ----------------
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found or cannot delete global category")


    from decimal import Decimal
    from typing import cast

    current_balance: Decimal = cast(Decimal, current_user.initial_balance)

    for expense in category.expenses:
        if expense.user_id == current_user.id:
            current_balance += Decimal(str(expense.amount))

 
    current_user.initial_balance = current_balance  # type: ignore
    db.add(current_user)

    db.delete(category)
    db.commit()

    return {"detail": "Category and its expenses deleted, amounts refunded"}


