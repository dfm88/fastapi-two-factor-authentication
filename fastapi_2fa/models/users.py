from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false

from fastapi_2fa.db.base_class import Base
from fastapi_2fa.models.device import Device


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tfa_enabled = Column(Boolean, server_default=false(), index=True)
    device = relationship(Device, back_populates="user", uselist=False, lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"full_name={self.full_name}, "
            f")>"
        )
