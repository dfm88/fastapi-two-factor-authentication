from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from fastapi_2fa.api.deps.db import get_db
from fastapi_2fa.core.config import settings
from fastapi_2fa.crud.users import user_crud
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.jwt_token_schema import JwtTokenPayload

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", scheme_name="JWT"
)


async def _get_user_from_jwt(
    key: str,
    token: str,
    db: Session,
    expire_err_message: str = "Token expired",
    jwt_err_message: str = "Could not validate credentials, "
                           "if TFA is enabled, please confirm token first",
):
    try:
        payload = jwt.decode(token=token, key=key, algorithms=[settings.ALGORITHM])
        token_data = JwtTokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=expire_err_message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=jwt_err_message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_crud.get(db=db, id=token_data.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user


async def get_authenticated_user(
    token: str = Depends(reuseable_oauth),
    db: Session = Depends(get_db),
) -> User:
    return await _get_user_from_jwt(key=settings.JWT_SECRET_KEY, token=token, db=db)


async def get_authenticated_user_pre_tfa(
    token: str = Depends(reuseable_oauth),
    db: Session = Depends(get_db),
) -> User:
    return await _get_user_from_jwt(
        token=token,
        key=settings.PRE_TFA_SECRET_KEY,
        db=db,
        expire_err_message="Token expired, login again "
        "and validate TFA token within "
        f"{settings.PRE_TFA_TOKEN_EXPIRE_MINUTES} minutes",
    )
