from typing import Generator

import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from fastapi_2fa.core.config import TestingConfig
from fastapi_2fa.db.base import Base

__all__ = (
    'async_session',
)

test_settings = TestingConfig()

# ASYNC DB SESSION AND ENGINE
async_engine = create_async_engine(
    test_settings.SQLALCHEMY_DATABASE_URI,
    future=True,
    echo=True,
)
TestingAsyncSessionLocal = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

# SYNC DB SESSION AND ENGINE
sync_engine = create_engine(
    test_settings.SQLALCHEMY_DATABASE_TEST_SYNC_URI,  # Sqlite test db
    connect_args=test_settings.DATABASE_CONNECT_DICT
)
TestingSyncSessionLocal = sessionmaker(
    autocommit=True,
    autoflush=True,
    bind=sync_engine
)


@pytest_asyncio.fixture(scope="module")
async def async_session() -> AsyncSession:
    session = TestingAsyncSessionLocal

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


async def override_get_db() -> Generator:
    try:
        db_sess = TestingAsyncSessionLocal()
        yield db_sess
        await db_sess.commit()
        print('committed in test db...')
    except Exception as ex:
        print(f'rolling db for exception {ex} ...')
        await db_sess.rollback()
    finally:
        print('closing test db...')
        await db_sess.close()
        print('..test db closed!')


# # For testing sync DB
# @pytest.fixture(scope='session')
# async def test_db() -> Generator:
#     # before each test create the db ...
#     Base.metadata.create_all(bind=engine)
#     yield TestingAsyncSessionLocal()
#     # ... and drop it after
#     # https://stackoverflow.com/questions/67255653/how-to-set-up-and-tear-down-a-database-between-tests-in-fastapi  # noqa
#     Base.metadata.drop_all(bind=engine)
