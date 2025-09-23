import logging

from fastapi import Request, HTTPException, status
from src.schemas.user import AuthUser
from src.core import config
from jwt import PyJWTError
import jwt


def get_current_user(request: Request) -> AuthUser:
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        payload = jwt.decode(
            token[7:], config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        logging.info(f"[get_current_user] payload: {payload}")
        user = AuthUser(
            user_id=payload.get("sub"),
            expire=payload.get("exp"),
        )
        if not user.user_id:
            raise ValueError("Invalid token: no user_id")
        return user
    except (PyJWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authorization error: {str(e)}",
        )
