from fastapi import APIRouter, Depends

from app.models.users import User
from app.schemas.users import UserResponse
from app.utils.oauth2 import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

