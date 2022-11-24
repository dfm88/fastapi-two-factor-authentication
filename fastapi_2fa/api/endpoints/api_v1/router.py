from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from fastapi_2fa.api.deps.db import get_db


user_router = APIRouter()


@user_router.get('/users')
async def get_user(
    db: Session = Depends(get_db),
) -> Any:
    return {'user': 'ok'}
