import typing as t

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id = Column(Integer, primary_key=True, index=True)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
