import asyncio
from typing import Generator
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from fastapi_2fa.api.deps.db import get_db
from fastapi_2fa.main import app
from tests import factories
from tests.factories.db_factory import override_get_db

# override get_db dependency
app.dependency_overrides[get_db] = override_get_db

# # register fixtures from factories
async_session = factories.async_session

user_factory_no_tfa_factory = factories.user_factory_no_tfa_factory
user_with_email_device_factory = factories.user_with_email_device_factory
user_with_cod_gen_device_factory = factories.user_with_cod_gen_device_factory

user_data_no_tfa = factories.user_data_no_tfa
user_data_tfa_email_fixture = factories.user_data_tfa_email_fixture
user_data_tfa_code_gen_fixture = factories.user_data_tfa_code_gen_fixture


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def test_client() -> Generator:
    yield AsyncClient(app=app, base_url="http://test")


@pytest.fixture(autouse=True)
def test_env(monkeypatch):
    monkeypatch.setenv("FASTAPI_CONFIG", "testing")


# patch celery task
@pytest.fixture(scope='function')
def mock_celery_send_mail():
    with patch("fastapi_2fa.core.utils.send_email_task.apply_async", autospec=True) as m:
        m.return_value = {}
        yield m
