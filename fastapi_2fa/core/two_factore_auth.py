import pyotp

from fastapi_2fa.models.device import BackupToken, Device
from fastapi_2fa.models.users import User


async def create_device_for_user(user: User):
    ...
