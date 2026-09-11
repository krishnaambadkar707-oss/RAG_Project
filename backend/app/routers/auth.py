from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas import UserCreate, UserResponse, Token, LoginRequest
from app.services.auth_service import (
    create_user, get_user_by_email, verify_password, create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")
    user = create_user(db, user_data)
    return user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user
