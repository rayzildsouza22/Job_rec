from fastapi import Depends, HTTPException, status

from app.models.users import User
from app.utils.oauth2 import get_current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency: only allow admin users through."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
