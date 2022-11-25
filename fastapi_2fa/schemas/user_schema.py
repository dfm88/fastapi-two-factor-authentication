from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, root_validator

from fastapi_2fa.schemas.device_schema import DeviceCreate, DeviceInDBBase


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    tfa_enabled: Optional[bool] = False
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    device: Optional[DeviceCreate] = None

    @root_validator(pre=True)
    def check_device_if_tfa_enabled(cls, values):
        if values['tfa_enabled'] and values['device'] is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                'when enabling two factor authentication, '
                'also a device_type should be provided'
            )
        return values


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    tfa_enabled: Optional[bool] = False
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None
    device: Optional[DeviceInDBBase] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class UserOut(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
