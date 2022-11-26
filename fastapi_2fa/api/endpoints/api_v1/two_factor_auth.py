from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from fastapi_2fa.api.deps.db import get_db
from fastapi_2fa.api.deps.users import (get_authenticated_user,
                                        get_authenticated_user_pre_tfa)
from fastapi_2fa.core import security
from fastapi_2fa.core.enums import DeviceTypeEnum
from fastapi_2fa.core.two_factor_auth import (qr_code_from_key,
                                              verify_backup_token,
                                              verify_token)
from fastapi_2fa.core.utils import send_mail_backup_tokens
from fastapi_2fa.crud.backup_token import backup_token_crud
from fastapi_2fa.crud.device import device_crud
from fastapi_2fa.crud.users import user_crud
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.device_schema import DeviceCreate
from fastapi_2fa.schemas.jwt_token_schema import JwtTokenSchema
from fastapi_2fa.schemas.user_schema import UserUpdate

tfa_router = APIRouter()


@tfa_router.post(
    "/login_tfa",
    summary="Verify two factor authentication token",
    response_model=JwtTokenSchema,
)
async def login_tfa(
    tfa_token: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_authenticated_user_pre_tfa),
) -> Any:
    if verify_token(user=user, token=tfa_token):
        return JwtTokenSchema(
            access_token=security.create_jwt_access_token(user.id),
            refresh_token=security.create_jwt_refresh_token(user.id),
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="TOTP token mismatch"
    )


@tfa_router.post(
    "/recover_tfa",
    summary="Checks and consumes one of the user's backup tokens re initializing",
    response_model=JwtTokenSchema,
)
async def recover_tfa(
    tfa_backup_token: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_authenticated_user_pre_tfa),
) -> Any:
    if backup_tokens := await backup_token_crud.get_user_backup_tokens(
        db=db,
        user=user
    ):
        matched_bkp_token = verify_backup_token(
            backup_tokens=backup_tokens,
            tfa_backup_token=tfa_backup_token
        )

        if matched_bkp_token:
            print('..consuming backup token')
            await backup_token_crud.remove(
                db=db, id=matched_bkp_token.id
            )
            return JwtTokenSchema(
                access_token=security.create_jwt_access_token(user.id),
                refresh_token=security.create_jwt_refresh_token(user.id),
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TOTP backup token not found"
        )

    # user has elapsed all backup tokens
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user.email} has elapsed his backup tokens, "
               "please contact the system administrator"
    )


@tfa_router.get(
    "/get_my_qrcode",
    summary="Returns authenticated user's qr_code "
            "if user's device is of type 'code_generator'",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns no content or a qr code "
                           "if tfas is enabled and device_type "
                           "is 'code_generator'",
        }
    },
)
async def get_my_qrcode(
    user: User = Depends(get_authenticated_user),
) -> Any:
    if (
        user.tfa_enabled and
        user_crud.device.device_type == DeviceTypeEnum.CODE_GENERATOR
    ):
        qr_code = qr_code_from_key(
            encoded_key=user.device.key,
            user_email=user.email
        )
        return StreamingResponse(content=qr_code, media_type="image/png")

    # user has elapsed all backup tokens
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"User {user.email} has not tfa enabled or "
               "has not a 'code_generator' device"
    )


@tfa_router.put(
    "/enable_tfa",
    summary="Enable two factor authentication for registered user",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns no content or a qr code "
                           "if device_type is 'code_generator'",
        }
    },
)
async def enable_tfa(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_authenticated_user),
) -> Any:
    if not user.tfa_enabled:
        user = await user_crud(transaction=True).update(
            db=db,
            db_obj=user,
            obj_in=UserUpdate(tfa_enabled=True)
        )
        device, qr_code = await device_crud(transaction=True).create(
            db=db,
            device=device,
            user=user
        )

        send_mail_backup_tokens(user=user, device=device)

        if device.device_type == DeviceTypeEnum.CODE_GENERATOR:
            return StreamingResponse(content=qr_code, media_type="image/png")

        return Response(status_code=status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Two factor authentication already '
               f'active for user {user.email}'
    )
