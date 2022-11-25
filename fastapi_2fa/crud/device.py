from typing import Any

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_2fa.core.two_factor_auth import create_device_for_user
from fastapi_2fa.crud.base_crud import CrudBase
from fastapi_2fa.models.device import BackupToken, Device
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.device_schema import DeviceCreate, DeviceUpdate


class DeviceCrud(CrudBase[Device, DeviceCreate, DeviceUpdate]):
    @staticmethod
    async def create(db: Session, device: DeviceCreate) -> Device:
        db_obj = Device(
            email=device.email,
            hashed_password=get_password_hash(device.password),
            tfa_enabled=device.tfa_enabled,
            full_name=device.full_name,
        )
        db.add(db_obj)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: Session, db_obj: Device, obj_in: DeviceUpdate | dict[str, Any]
    ) -> Device:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db=db, db_obj=db_obj, obj_in=obj_in)


device_crud = DeviceCrud(model=Device)
