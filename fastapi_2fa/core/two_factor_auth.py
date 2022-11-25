import io
import random
from typing import Iterator

import pyotp
import qrcode
from fernet import Fernet

from fastapi_2fa.core.config import settings

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


def verify_token(user: User, token:str) -> bool:
    assert user.tfa_enabled is True, 'User does not have TFA enabled'
    assert user.device is not None, 'User has no associated device'
    decoded_key = _fernet_decode(value=user.device.key)
    totp = pyotp.TOTP(decoded_key)
    result =  totp.verify(token, valid_window=settings.TOTP_TOKEN_TOLERANCE)
    return result


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
