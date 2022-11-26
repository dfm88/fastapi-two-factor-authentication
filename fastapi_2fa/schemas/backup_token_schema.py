from typing import Optional

from pydantic import BaseModel


# Shared properties
class BackupTokenBase(BaseModel):
    token: str


# Properties to receive via API on creation
class BackupTokenCreate(BackupTokenBase):
    device_id: Optional[int]


# Properties to receive via API on update
class BackupTokenUpdate(BackupTokenBase):
    pass


class BackupTokenInDBBase(BackupTokenBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class BackupTokenInDb(BackupTokenInDBBase):
    pass


class BackupTokenOut(BackupTokenInDb):
    pass
