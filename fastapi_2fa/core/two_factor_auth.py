import io
import random
from typing import Iterator

import pyotp
import qrcode
from fernet import Fernet

from fastapi_2fa.core.config import settings
from fastapi_2fa.core.enums import DeviceTypeEnum
from fastapi_2fa.core.utils import send_mail_totp_token
from fastapi_2fa.models.device import BackupToken
from fastapi_2fa.models.users import User

ENCODING = 'utf-8'


def _get_fernet_hash_key() -> Fernet:
    return Fernet(
        key=bytes(settings.FERNET_KEY_TFA_TOKEN, ENCODING)
    )


def _fernet_encode(value: str) -> str:
    hash_key = _get_fernet_hash_key()
    return hash_key.encrypt(value.encode()).decode(ENCODING)


def _fernet_decode(value: str) -> str:
    hash_key = _get_fernet_hash_key()
    return hash_key.decrypt(value.encode()).decode(ENCODING)


def create_encoded_two_factor_auth_key() -> str:
    base_key = pyotp.random_base32()
    return _fernet_encode(value=base_key)


def get_decoded_two_factor_auth_key(value: str) -> str:
    return _fernet_decode(value=value)


def get_fake_otp_tokens(
    nr_digits: int = settings.TFA_TOKEN_LENGTH,
    nr_tokens: int = settings.TFA_BACKUP_TOKENS_NR
) -> Iterator[str]:
    for _ in range(nr_tokens):
        random_otp = ''.join(
            str(random.randint(0, 9)) for _ in range(nr_digits)
        )
        yield random_otp



def get_current_totp(user: User) -> pyotp.TOTP:
    assert user.tfa_enabled is True, 'User does not have TFA enabled'
    assert user.device is not None, 'User has no associated device'
    decoded_key = _fernet_decode(value=user.device.key)
    return pyotp.TOTP(decoded_key)


def verify_token(user: User, token: str) -> bool:
    totp: pyotp.TOTP = get_current_totp(user=user)
    result = totp.verify(token, valid_window=settings.TOTP_TOKEN_TOLERANCE)
    return result


def verify_backup_token(
    backup_tokens: list[BackupToken], tfa_backup_token: str
) -> BackupToken | None:
    """Checks between "backup_tokens" if there is the "tfa_backup_token"

    Args:
        backup_tokens list[BackupToken]
        tfa_backup_token (str)

    Returns:
        BackupToken | None: the matched BackupToken or None if no backup tokens matched
    """
    for bkp_token in backup_tokens:
        if bkp_token.token == tfa_backup_token:
            # consume backup token and return access jwt
            print('Found backup token match..')
            return bkp_token


def send_tfa_token(
    user: User,
    device_type: DeviceTypeEnum
) -> None:
    if device_type == DeviceTypeEnum.EMAIL:
        totp: pyotp.TOTP = get_current_totp(user=user)
        current_totp = totp.now()
        send_mail_totp_token(
            user=user,
            token=current_totp
        )


def qr_code_from_key(encoded_key: str, user_email: str):
    decoded_key = _fernet_decode(value=encoded_key)
    qrcode_key = pyotp.TOTP(
        decoded_key, interval=settings.TOTP_TOKEN_TOLERANCE
    ).provisioning_uri(user_email, issuer_name=settings.TOTP_ISSUER_NAME)
    img = qrcode.make(qrcode_key)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
