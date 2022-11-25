import random
from typing import Iterator

import pyotp
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
