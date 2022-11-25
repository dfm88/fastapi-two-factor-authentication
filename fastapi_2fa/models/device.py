from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from fastapi_2fa.core import enums
from fastapi_2fa.db.base_class import Base


# @declarative_mixin
class Device(Base):
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    device_type = Column(
        postgresql.ENUM(enums.DeviceTypeEnum), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="device", uselist=False, lazy="joined")
    backup_tokens = relationship(
        "BackupToken",
        back_populates="device",
        uselist=True,
    )


class BackupToken(Base):
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("device.id"))
    device = relationship("Device", back_populates="backup_tokens", uselist=True)
    token = Column(String(length=8))
