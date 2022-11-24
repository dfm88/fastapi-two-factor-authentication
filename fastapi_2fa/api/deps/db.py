from typing import Generator

from fastapi_2fa.db.session import SessionLocal


async def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        await db.close()
