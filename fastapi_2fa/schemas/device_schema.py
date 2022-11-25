from typing import Optional

from core.enums import DeviceTypeEnum
from pydantic import BaseModel


# Shared properties
class DeviceBase(BaseModel):
    device_type: DeviceTypeEnum


# Properties to receive via API on creation
class DeviceCreate(DeviceBase):
    pass


# Properties to receive via API on update
class DeviceUpdate(DeviceBase):
    pass


class DeviceInDBBase(DeviceBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class DeviceInDb(DeviceInDBBase):
    key: str
