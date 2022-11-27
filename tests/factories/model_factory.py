import factory
import pytest
from factory import fuzzy

from fastapi_2fa.core import enums
from fastapi_2fa.core.security import get_password_hash
from fastapi_2fa.core.two_factor_auth import (
    _get_fake_otp_token, create_encoded_two_factor_auth_key)
from fastapi_2fa.models.device import BackupToken, Device
from fastapi_2fa.models.users import User

from .db_factory import TestingSyncSessionLocal

__all__ = (
    "user_factory_no_tfa_factory",
    "user_with_email_device_factory",
    "user_with_cod_gen_device_factory",
    "device_factory",
    "email_device_factory",
    "code_gen_device_factory",
    "backup_token_factory",
)


session = TestingSyncSessionLocal()


class DeviceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Device
        sqlalchemy_session = session
        sqlalchemy_session_persistence = 'flush'

    device_type = fuzzy.FuzzyChoice(
        [enums.DeviceTypeEnum.EMAIL, enums.DeviceTypeEnum.CODE_GENERATOR]
    )
    backup_tokens = factory.RelatedFactoryList(
        'tests.factories.model_factory.BackupTokenFactory', 'device', size=5
    )

    @factory.lazy_attribute
    def key(self):
        return create_encoded_two_factor_auth_key()


class EmailDeviceFactory(DeviceFactory):
    device_type = enums.DeviceTypeEnum.EMAIL


class CodeGenDeviceFactory(DeviceFactory):
    device_type = enums.DeviceTypeEnum.CODE_GENERATOR


class BackupTokenFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BackupToken
        sqlalchemy_session = session
        sqlalchemy_session_persistence = 'flush'

    device = factory.SubFactory(DeviceFactory)

    @factory.lazy_attribute
    def token(self):
        return _get_fake_otp_token()


class UserFactoryNoTfa(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = session
        sqlalchemy_session_persistence = 'flush'
        sqlalchemy_get_or_create = ('email',)
        exclude = ('password', )

    full_name = factory.Sequence(lambda n: f"test_user{n+1}")
    email = factory.Sequence(lambda n: f"test_user{n+1}@mail.com")
    tfa_enabled = False
    password = '123456'

    @factory.lazy_attribute
    def hashed_password(self):
        return get_password_hash(self.password)


class UserEmailDeviceFactory(UserFactoryNoTfa):
    tfa_enabled = True
    device = factory.SubFactory(EmailDeviceFactory)


class UserCodGenDeviceFactory(UserFactoryNoTfa):
    tfa_enabled = True
    device = factory.SubFactory(CodeGenDeviceFactory)


@pytest.fixture
def user_factory_no_tfa_factory():
    yield UserFactoryNoTfa


@pytest.fixture
def user_with_email_device_factory():
    yield UserEmailDeviceFactory


@pytest.fixture
def user_with_cod_gen_device_factory():
    yield UserCodGenDeviceFactory


@pytest.fixture
def device_factory():
    yield DeviceFactory


@pytest.fixture
def email_device_factory():
    yield EmailDeviceFactory


@pytest.fixture
def code_gen_device_factory():
    yield CodeGenDeviceFactory


@pytest.fixture
def backup_token_factory():
    yield BackupTokenFactory
