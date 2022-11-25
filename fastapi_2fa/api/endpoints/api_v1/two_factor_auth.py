from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from fastapi_2fa.api.deps.db import get_db
from fastapi_2fa.api.deps.users import get_authenticated_user
from fastapi_2fa.core.enums import DeviceTypeEnum
from fastapi_2fa.core.utils import send_backup_tokens
from fastapi_2fa.crud.device import device_crud
from fastapi_2fa.crud.users import user_crud
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.device_schema import DeviceCreate
from fastapi_2fa.schemas.user_schema import UserUpdate

tfa_router = APIRouter()


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
    if not user_crud(transaction=True).is_tfa_enabled(user):
        user = await user_crud.update(
            db=db,
            db_obj=user,
            obj_in=UserUpdate(tfa_enabled=True)
        )
        device, qr_code = await device_crud(transaction=True).create(
            db=db,
            device=device,
            user=user
        )

        send_backup_tokens(user=user, device=device)

        if device.device_type == DeviceTypeEnum.CODE_GENERATOR:
            return StreamingResponse(content=qr_code, media_type="image/png")

        return Response(status_code=status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Two factor authentication already '
               f'active for user {user.email}'
    )
