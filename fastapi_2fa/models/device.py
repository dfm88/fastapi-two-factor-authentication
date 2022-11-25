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

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"device_type={self.device_type}, "
            f"user={self.user.full_name}, "
            f")>"
        )


class BackupToken(Base):
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("device.id"))
    device = relationship("Device", back_populates="backup_tokens", uselist=False)
    token = Column(String(length=8))

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"device={self.device}, "
            f")>"
        )
