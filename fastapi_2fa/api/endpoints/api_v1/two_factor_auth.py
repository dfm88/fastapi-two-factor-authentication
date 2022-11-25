from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi_2fa.api.deps.db import get_db
from fastapi_2fa.api.deps.users import get_authenticated_user
from fastapi_2fa.crud.device import device_crud
from fastapi_2fa.crud.users import user_crud
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.device_schema import DeviceCreate
from fastapi_2fa.schemas.user_schema import UserOut, UserUpdate

tfa_router = APIRouter()


@tfa_router.put(
    "/enable_tfa",
    summary="Enable two factor authentication for registered user",
    response_model=UserOut,
)
async def enable_tfa(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_authenticated_user),
) -> Any:
    if not user_crud.is_tfa_enabled(user):
        async with db.begin_nested():
            user = await user_crud.update(
                db=db,
                db_obj=user,
                obj_in=UserUpdate(tfa_enabled=True)
            )
            await device_crud.create(
                db=db,
                device=device,
                user=user
            )
    await db.refresh(user)
    return user
