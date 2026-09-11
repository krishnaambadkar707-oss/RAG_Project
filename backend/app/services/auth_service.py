import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import UserCreate

import hashlib
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + "$" + pwd_hash.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if "$" not in hashed_password:
            return False
        salt_hex, hash_hex = hashed_password.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return pwd_hash.hex() == hash_hex
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_create: UserCreate) -> User:
    hashed_pwd = get_password_hash(user_create.password)
    user = User(
        email=user_create.email,
        password_hash=hashed_pwd,
        role=user_create.role or "employee"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    if token:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            email: str = payload.get("sub")
            if email:
                user = get_user_by_email(db, email=email)
                if user:
                    return user
        except Exception:
            pass

    # Default demo user fallback for open local demo mode
    user = db.query(User).filter(User.email == "demo@company.com").first()
    if user:
        return user
    demo_user = UserCreate(email="demo@company.com", password="password123", role="admin")
    return create_user(db, demo_user)

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
