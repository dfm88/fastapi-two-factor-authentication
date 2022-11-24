from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from fastapi_2fa.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(
    subject: str | Any,
    refresh: bool = False,
    expires_delta: int = None
) -> str:
    """
    Create access or refresh token
    """
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        minutes = settings.REFRESH_TOKEN_EXPIRE_MINUTES if refresh \
            else settings.ACCESS_TOKEN_EXPIRE_MINUTES
        expires_delta = datetime.utcnow() + timedelta(
            minutes=minutes
        )
    to_encode = {
        "sub": str(subject),
        "exp": expires_delta,
    }

    key = settings.JWT_SECRET_KEY_REFRESH if refresh \
        else settings.JWT_SECRET_KEY

    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=key,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt
