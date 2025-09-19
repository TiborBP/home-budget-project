from fastapi import FastAPI
from .database import engine, Base
from .routers import categories, expenses, auth
from sqlalchemy.orm import Session
from . import models, database



Base.metadata.create_all(bind=engine)


PRESET_CATEGORIES = ["food", "car", "recreation"]

def create_preset_categories():
    db: Session = database.SessionLocal()
    try:
        for name in PRESET_CATEGORIES:
            exists = db.query(models.Category).filter(models.Category.name == name, models.Category.user_id == None).first()
            if not exists:
                db.add(models.Category(name=name))
        db.commit()
    finally:
        db.close()

create_preset_categories()


app = FastAPI(title="Home Budget API", version="1.0.0")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)

