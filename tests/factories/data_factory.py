from typing import Type

import pytest

from fastapi_2fa.core.two_factor_auth import get_current_totp
from tests.factories.model_factory import UserFactoryBase

__all__ = (
    "user_data_no_tfa",
    "user_data_tfa_email_fixture",
    "user_data_tfa_code_gen_fixture",
    "correct_totp_token_for_user",
    "wrong_totp_token_for_user",
    "correct_bkp_token_for_user",
)


@pytest.fixture
def user_data_no_tfa() -> dict:
    yield {
        "email": "test_no_tfa@mail.com",
        "tfa_enabled": False,
        "full_name": "diego",
        "password": 123456,
        "device": {
            "device_type": "email"
        }
    }


@pytest.fixture
def user_data_tfa_email_fixture(user_data_no_tfa) -> dict:
    user_data_no_tfa.update(
        {
            "email": "test_tfa_email@mail.com",
            "tfa_enabled": True,
            "device": {
                "device_type": "email"
            }
        }
    )
    yield user_data_no_tfa


@pytest.fixture
def user_data_tfa_code_gen_fixture(user_data_no_tfa) -> dict:
    user_data_no_tfa.update(
        {
            "email": "test_tfa_code_gen@mail.com",
            "tfa_enabled": True,
            "device": {
                "device_type": "code_generator"
            }
        }
    )
    yield user_data_no_tfa


@pytest.fixture
def correct_totp_token_for_user() -> str:
    def _correct_totp_token_for_user(user: Type[UserFactoryBase]):
        return get_current_totp(user).now()
    yield _correct_totp_token_for_user


@pytest.fixture
def wrong_totp_token_for_user() -> str:
    def _wrong_totp_token_for_user(user: Type[UserFactoryBase]):
        return '000000'
    yield _wrong_totp_token_for_user


@pytest.fixture
def correct_bkp_token_for_user() -> str:
    def _correct_bkp_token_for_user(user: Type[UserFactoryBase]):
        bkp_token = user.device.backup_tokens.pop()
        return bkp_token.token
    yield _correct_bkp_token_for_user
