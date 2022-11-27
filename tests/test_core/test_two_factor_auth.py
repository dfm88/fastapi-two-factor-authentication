import hypothesis
import pyotp
import pytest

from fastapi_2fa.core import two_factor_auth


@hypothesis.given(hypothesis.strategies.text())
def test_fernet_encode_decode(s):
    encoded = two_factor_auth._fernet_encode(s)
    decoded = two_factor_auth._fernet_decode(encoded)
    assert decoded == s


def test_get_current_user_totp(
    async_session, user_with_email_device_factory, user_factory_no_tfa_factory
):
    user_without_tfa = user_factory_no_tfa_factory.create()
    with pytest.raises(AssertionError):
        two_factor_auth.get_current_totp(user_without_tfa)

    user_with_tfa = user_with_email_device_factory.create()
    totp = two_factor_auth.get_current_totp(user_with_tfa)
    assert isinstance(totp, pyotp.TOTP)
