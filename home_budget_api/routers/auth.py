from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, database
from decimal import Decimal
from typing import Any, cast


# ---------------- PASSWORD & JWT SETUP ----------------
SECRET_KEY = "iVdzQLqUiX"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- AUTH ROUTER ----------------
router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------- REGISTER ----------------
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if username exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    # Create user in db
    db_user = models.User(
        username=user.username,
        password_hash=hash_password(user.password),
        initial_balance=1000.0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---------------- LOGIN ----------------
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------- GET CURRENT USER ----------------
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


# ---------------- UPDATE USER BALANCE ----------------
@router.patch("/me/balance", response_model=schemas.UserResponse)
def update_balance(
    balance_update: schemas.BalanceUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Ensure current_user is fresh
    db.refresh(current_user)

    # Work in Decimal for money
    current_balance: Decimal = cast(Decimal, current_user.initial_balance)
    amount_to_add = Decimal(str(balance_update.amount))

    if current_balance + amount_to_add < Decimal("0"):
        raise HTTPException(status_code=400, detail="Insufficient balance")

    new_balance = current_balance + amount_to_add

    # Tell the type checker to treat current_user as Any for assignment
    user_any = cast(Any, current_user)
    user_any.initial_balance = new_balance

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


# ---------------- VIEW CURRENT USER BALANCE ----------------
@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns the currently logged-in user's profile for easy viewing of balance.
    """
    db.refresh(current_user)  # make sure we have fresh data from DB
    return current_user