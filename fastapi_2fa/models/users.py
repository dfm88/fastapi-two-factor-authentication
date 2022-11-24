from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from fastapi_2fa.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tfa_enabled = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"full_name={self.full_name}, "
            f"tfa_enabled={self.tfa_enabled}, "
            f")>"
        )