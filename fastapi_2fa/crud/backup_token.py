from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from fastapi_2fa.crud.base_crud import CrudBase
from fastapi_2fa.models.device import BackupToken, Device
from fastapi_2fa.models.users import User
from fastapi_2fa.schemas.backup_token_schema import (BackupTokenCreate,
                                                     BackupTokenUpdate)


class BackupTokenCrud(CrudBase[Device, BackupTokenCreate, BackupTokenUpdate]):

    @staticmethod
    async def get_user_backup_tokens(db: Session, user: User) -> list:
        if not user.device:
            return []
        result = await db.execute(
            select(Device).where(
                Device.id == user.device.id
            ).options(joinedload(Device.backup_tokens))
        )
        device_with_bkp_tokens: Device = result.scalar()
        return device_with_bkp_tokens.backup_tokens


backup_token_crud = BackupTokenCrud(model=BackupToken)
