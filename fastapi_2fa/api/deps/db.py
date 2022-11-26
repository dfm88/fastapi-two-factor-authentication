from typing import Generator

from fastapi_2fa.db.session import SessionLocal


async def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
        await db.commit()
        print('committed in db...')
    except Exception as ex:
        print(f'rolling db for exception {ex} ...')
        await db.rollback()
    finally:
        print('closing db...')
        await db.close()
        print('..db closed!')
