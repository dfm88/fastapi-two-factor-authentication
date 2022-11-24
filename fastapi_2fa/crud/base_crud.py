from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from fastapi_2fa.db.base_class import Base

# SqlAlchemy Model
ModelType = TypeVar("ModelType", bound=Base)
# Pydantic Create schema
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Pydantic Update schema
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CrudBase(
    Generic[
        ModelType,  # XXX SqlAlchemy Model,
        CreateSchemaType,  # Pydantic Create Schema,
        UpdateSchemaType,  # Pydantic Update Schema
    ]
):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: Session, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        model_query = await db.execute(query)
        (model_instance,) = model_query.first()
        return model_instance

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        model_list = await db.execute(select(self.model).offset(skip).limit(limit))
        return model_list.scalars().all()

    async def create(self, db: Session, *, obj_in: CreateSchemaType):
        obj_in_data = jsonable_encoder(obj_in)
        db_obj: ModelType = self.model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        query = (
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        try:
            # commit only if not under transaction
            if not db.in_nested_transaction():
                await db.commit()
            return db_obj
        except Exception as ex:
            await db.rollback()
            raise ex

    async def remove(self, db: Session, *, id: int) -> bool:
        query = delete(self.model).where(self.model.id == id)
        await db.execute(query)
        try:
            await db.commit()
        except Exception as ex:
            await db.rollback()
            raise ex
        return True
