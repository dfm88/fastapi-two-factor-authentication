from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi_2fa.api.deps.db import get_db
from fastapi_2fa.crud.users import user_crud
from fastapi_2fa.schemas import user_schema

user_router = APIRouter()


@user_router.get("/users", response_model=list[user_schema.UserOut])
async def get_user(
    db: Session = Depends(get_db),
) -> Any:
    return await user_crud.get_multi(db=db)
