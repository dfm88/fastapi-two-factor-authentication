from typing import Any

from core.enums import DeviceTypeEnum
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_2fa.api.deps.db import get_db
from fastapi_2fa.api.deps.users import (
    get_authenticated_user,
    get_authenticated_user_pre_tfa,
)
from fastapi_2fa.core import security
from fastapi_2fa.core.config import settings
from fastapi_2fa.crud.users import user_crud
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.token_schema import TokenPayload, TokenSchema
from fastapi_2fa.schemas.user_schema import UserCreate, UserOut

auth_router = APIRouter()


@auth_router.post("/signup", summary="Create user", response_model=UserOut)
async def signup(
    db: Session = Depends(get_db), form_data: UserCreate = Depends()
) -> Any:
    try:
        user = await user_crud.create(
            db=db,
            user=form_data,
        )
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User with email "{form_data.email}" already exists',
        )


@auth_router.post(
    "/login",
    summary="Create access and refresh tokens for user",
    status_code=status.HTTP_200_OK,
    response_model=TokenSchema,
)
async def login(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = await user_crud.authenticate(
        db=db, email=form_data.username, password=form_data.password
    )

    # wrong credentials
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    # verify 2 factor authentication
    if user_crud.is_tfa_enabled(user=user):
        response.status_code = status.HTTP_202_ACCEPTED
        return TokenSchema(
            access_token=security.create_pre_tfa_token(user.id),
            refresh_token=None,
        )

    # create access and refresh tokens
    return TokenSchema(
        access_token=security.create_jwt_access_token(user.id),
        refresh_token=security.create_jwt_refresh_token(user.id),
    )


@auth_router.post(
    "/login/tfa",
    summary="Verify two factor authenticazion token",
    response_model=UserOut,
)
async def login_tfa(
    tfa_token: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_authenticated_user_pre_tfa),
) -> Any:
    print(f"{tfa_token}")
    return user


@auth_router.put(
    "/enable_tfa",
    summary="Enable two factor authentication for registered user",
    response_model=UserOut,
)
async def enable_tfa(
    device_type: DeviceTypeEnum,
    db: Session = Depends(get_db),
    user: User = Depends(get_authenticated_user),
) -> Any:
    print(f"{device_type}")
    return user


@auth_router.post(
    "/test-token", summary="Test if the access token is ok", response_model=UserOut
)
async def test_token(user: User = Depends(get_authenticated_user)):
    """
    First authenticated endpoint
    """
    return user


@auth_router.post("/refresh", summary="Refresh token", response_model=TokenSchema)
async def refresh_token(db: Session = Depends(get_db), refresh_token: str = Body(...)):
    try:
        payload = jwt.decode(
            token=refresh_token,
            key=settings.JWT_SECRET_KEY_REFRESH,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_crud.get(db, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token for user",
        )
    return {
        "access_token": security.create_token(user.id),
        "refresh_token": security.create_token(user.id, refresh=True),
    }
