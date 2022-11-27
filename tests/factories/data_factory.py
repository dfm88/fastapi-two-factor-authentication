import pytest

__all__ = (
    "user_data_no_tfa",
    "user_data_tfa_email_fixture",
    "user_data_tfa_code_gen_fixture",
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
