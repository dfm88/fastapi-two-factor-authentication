from sqlalchemy.orm import Session

from fastapi_2fa.core.two_factor_auth import (
    create_encoded_two_factor_auth_key, get_fake_otp_tokens)
from fastapi_2fa.crud.base_crud import CrudBase
from fastapi_2fa.models.device import BackupToken, Device
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.device_schema import DeviceCreate, DeviceUpdate


class DeviceCrud(CrudBase[Device, DeviceCreate, DeviceUpdate]):

    @staticmethod
    async def create(db: Session, device: DeviceCreate, user: User) -> Device:
        # create device
        db_device = Device(
            key=create_encoded_two_factor_auth_key(),
            user_id=user.id,
            device_type=device.device_type
        )
        # create backup tokens
        for token in get_fake_otp_tokens():
            token_db = BackupToken(
                device_id=db_device.id,
                token=token
            )
            db_device.backup_tokens.append(token_db)
        db.add(db_device)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        return db_device


device_crud = DeviceCrud(model=Device)
