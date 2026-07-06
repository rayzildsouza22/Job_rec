import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.schemas.users import TokenResponse, UserLogin, UserRegister, UserResponse
from app.utils.security import hash_password, verify_password
from app.utils.token import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Simple admin bootstrap: any user registered with this email becomes admin.
# Configure via ADMIN_EMAIL in backend/.env.
ADMIN_EMAIL = (os.getenv("ADMIN_EMAIL") or "").lower().strip()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserRegister, database: Session = Depends(get_db)):
    normalized_email = user_data.email.lower()
    existing_user = database.scalar(
        select(User).where(User.email == normalized_email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    new_user = User(
        name=user_data.name.strip(),
        email=normalized_email,
        hashed_password=hash_password(user_data.password),
        is_admin=(ADMIN_EMAIL != "" and normalized_email == ADMIN_EMAIL),
    )
    database.add(new_user)
    database.commit()
    database.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, database: Session = Depends(get_db)):
    user = database.scalar(
        select(User).where(User.email == user_data.email.lower())
    )
    if user is None or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

