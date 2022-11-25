from qrcode.image.svg import SvgImage
from sqlalchemy.orm import Session

from fastapi_2fa.core.enums import DeviceTypeEnum
from fastapi_2fa.core.two_factor_auth import (
    create_encoded_two_factor_auth_key, get_fake_otp_tokens, qr_code_from_key)
from fastapi_2fa.crud.base_crud import CrudBase
from fastapi_2fa.models.device import BackupToken, Device
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.device_schema import DeviceCreate, DeviceUpdate


class DeviceCrud(CrudBase[Device, DeviceCreate, DeviceUpdate]):

    async def create(
        self, db: Session, device: DeviceCreate, user: User
    ) -> tuple[Device, SvgImage | None]:
        # create device
        encoded_key: str = create_encoded_two_factor_auth_key()
        db_device = Device(
            key=encoded_key,
            user=user,
            device_type=device.device_type
        )
        # create backup tokens
        for token in get_fake_otp_tokens():
            token_db = BackupToken(
                device=db_device,
                token=token
            )
            db_device.backup_tokens.append(token_db)
        db.add(db_device)
        if await self.handle_commit(db):
            await db.refresh(db_device)

        # generate qr_code
        qr_code = None
        if device.device_type == DeviceTypeEnum.CODE_GENERATOR:
            qr_code = qr_code_from_key(
                encoded_key=encoded_key,
                user_email=user.email
            )
        return db_device, qr_code


device_crud = DeviceCrud(model=Device)
