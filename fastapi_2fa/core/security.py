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


def _create_token(
    subject: int | Any,
    expire_minutes: int,
    key: str,
) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = {
        "sub": str(subject),
        "exp": expires_delta,
    }

    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=key,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def create_jwt_access_token(subject: int | Any) -> str:
    return _create_token(
        subject=subject,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        key=settings.JWT_SECRET_KEY,
    )


def create_jwt_refresh_token(subject: int | Any) -> str:
    return _create_token(
        subject=subject,
        expire_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        key=settings.JWT_SECRET_KEY_REFRESH,
    )


def create_pre_tfa_token(subject: int | Any) -> str:
    return _create_token(
        subject=subject,
        expire_minutes=settings.PRE_TFA_TOKEN_EXPIRE_MINUTES,
        key=settings.PRE_TFA_SECRET_KEY,
    )
