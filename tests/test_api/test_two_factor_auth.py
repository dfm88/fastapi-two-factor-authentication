import pytest

from fastapi_2fa.api.deps.users import (get_authenticated_user,
                                        get_authenticated_user_pre_tfa)
from tests.conftest import app

LOGIN_TFA_URL = "/api/v1/tfa/login_tfa?tfa_token=%s"
RECOVER_TFA_URL = "/api/v1/tfa/recover_tfa?tfa_backup_token=%s"
ENABLE_TFA_URL = "/api/v1/tfa/enable_tfa"


@pytest.mark.parametrize(
    "mock_user,totp_token,expected_status,expected_jwt_access_in_response",
    [
        ('user_with_email_device_factory', 'wrong_totp_token_for_user', 403, False),
        ('user_with_email_device_factory', 'correct_totp_token_for_user', 200, True),
    ],
)
@pytest.mark.asyncio
async def test_login_tfa(
    mock_user,
    totp_token,
    expected_status,
    expected_jwt_access_in_response,
    test_client,
    request,
    async_session
):
    """
    GIVEN mock user model with tfa enabled

    WHEN login_tfa endpoint is called by a user with correct tfa token
    THEN expected_status is 200, and access token in response

    WHEN login_tfa endpoint is called by a user with wrong tfa token
    THEN expected_status is 403, and no access token in response
    """
    # evaluate fixture
    mock_user = request.getfixturevalue(mock_user)
    # create mock user
    user = mock_user.create()

    # get totp token from fixture
    totp_token = request.getfixturevalue(totp_token)(user)

    # override jwt authentication deps
    app.dependency_overrides[get_authenticated_user_pre_tfa] = lambda: user

    response = await test_client.post(
        LOGIN_TFA_URL % totp_token
    )
    assert response.status_code == expected_status
    assert (response.json().get('access_token') is not None) == expected_jwt_access_in_response

    # resetting the override of jwt authentication deps
    del app.dependency_overrides[get_authenticated_user_pre_tfa]


@pytest.mark.parametrize(
    "mock_user,totp_token,expected_status,expected_jwt_access_in_response,remained_bkp_tokens",
    [
        ('user_with_email_device_factory', 'wrong_totp_token_for_user', 403, False, 5),
        ('user_with_email_device_factory', 'correct_bkp_token_for_user', 200, True, 4),
    ],
)
@pytest.mark.asyncio
async def test_recover_tfa(
    mock_user,
    totp_token,
    expected_status,
    expected_jwt_access_in_response,
    remained_bkp_tokens,
    test_client,
    request,
    async_session
):
    """
    GIVEN mock user model with tfa enabled

    WHEN recover_tfa endpoint is called by a user with correct backup token
    THEN expected_status is 200, user has one less bkp token and access token in response

    WHEN recover_tfa endpoint is called by a user with wrong backup token
    THEN expected_status is 403, user has the same nr of bkp token and no access token in response
    """
    # evaluate fixture
    mock_user = request.getfixturevalue(mock_user)
    # create mock user
    user = mock_user.create()

    # get totp token from fixture
    tfa_backup_token = request.getfixturevalue(totp_token)(user)

    # override jwt authentication deps
    app.dependency_overrides[get_authenticated_user_pre_tfa] = lambda: user
    response = await test_client.post(
        RECOVER_TFA_URL % tfa_backup_token
    )
    assert response.status_code == expected_status
    assert (response.json().get('access_token') is not None) == expected_jwt_access_in_response
    assert len(user.device.backup_tokens) == remained_bkp_tokens

    # resetting the override of jwt authentication deps
    del app.dependency_overrides[get_authenticated_user_pre_tfa]


@pytest.mark.parametrize(
    "mock_user,device,expected_status,expected_content_type,celery_sent_bkp_tokens",
    [
        ('user_with_email_device_factory', 'email', 400, 'application/json', False),
        ('user_factory_no_tfa_factory', 'email', 200, None, True),
        ('user_factory_no_tfa_factory', 'code_generator', 200, 'image/png', True),
    ],
)
@pytest.mark.asyncio
async def test_enable_tfa(
    mock_user,
    device,
    expected_status,
    expected_content_type,
    celery_sent_bkp_tokens,
    test_client,
    request,
    mock_celery_send_mail,
    async_session
):
    """
    GIVEN mock user model

    WHEN enable_tfa endpoint is called by user with tfa already enabled
    THEN expected_status is 400, content_type is None and backup tokens email was not sent

    WHEN enable_tfa endpoint is called with an email device by user with no tfa enabled
    THEN expected_status is 200, content_type is None and backup tokens email was sent

    WHEN enable_tfa endpoint is called with an email device by user with no tfa enabled
    THEN expected_status is 200, content_type is 'image/png' backup tokens email and tfa
         tokens was sent
    """
    # evaluate fixture
    mock_user = request.getfixturevalue(mock_user)

    # from fastapi_2fa.crud.backup_token import backup_token_crud
    # aa = await backup_token_crud.get_multi(async_session)
    # create mock user
    user = mock_user.create()

    # override jwt authentication deps
    app.dependency_overrides[get_authenticated_user] = lambda: user

    response = await test_client.put(
        ENABLE_TFA_URL,
        json={
            'device_type': device
        }
    )
    assert response.status_code == expected_status
    assert response.headers.get('content-type') == expected_content_type
    assert mock_celery_send_mail.called == celery_sent_bkp_tokens

    # resetting the override of jwt authentication deps
    del app.dependency_overrides[get_authenticated_user]
