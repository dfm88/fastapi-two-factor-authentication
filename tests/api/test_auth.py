import pytest


SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
TEST_JWT_TOKEN = "/api/v1/auth/test-token"


@pytest.mark.parametrize(
    "input_data,expected_status,expected_content_type,celery_sent_bkp_tokens",
    [
        ('user_data_no_tfa', 200, None, False),
        ('user_data_tfa_email_fixture', 200, None, True),
        ('user_data_tfa_code_gen_fixture', 200, 'image/png', True),
    ],
)
@pytest.mark.asyncio
async def test_signup(
    input_data,
    expected_status,
    expected_content_type,
    celery_sent_bkp_tokens,
    test_client,
    request,
    mock_celery_send_mail,
    async_session
):
    """
    GIVEN user json data

    WHEN signup endpoint is called with data with tfa disabled
    THEN expected_status is 200, content_type is None and no bkp tfa tokens was sent

    WHEN signup endpoint is called with data with tfa enabled and email device
    THEN expected_status is 200, content_type is None and bkp tfa tokens was sent

    WHEN signup endpoint is called with data with tfa enabled and code gen device
    THEN expected_status is 200, content_type is 'image/png' and bkp tfa tokens was sent
    """
    response = await test_client.post(
        SIGNUP_URL,
        json=request.getfixturevalue(input_data)
    )
    assert response.status_code == expected_status
    assert response.headers.get('content-type') == expected_content_type
    assert mock_celery_send_mail.called == celery_sent_bkp_tokens


@pytest.mark.parametrize(
    "mock_user,expected_status,expected_jwt_access_in_response,"
    "expected_jwt_refresh_in_response,celery_sent_tfa_token",
    [
        ('user_factory_no_tfa_factory', 200, True, True, False),
        ('user_with_cod_gen_device_factory', 202, True, False, False),
        ('user_with_email_device_factory', 202, True, False, True),
    ],
)
@pytest.mark.asyncio
async def test_login_response(
    mock_user,
    expected_status,
    expected_jwt_access_in_response,
    expected_jwt_refresh_in_response,
    celery_sent_tfa_token,
    test_client,
    request,
    mock_celery_send_mail,
    async_session
):
    """
    GIVEN mock user model

    WHEN login endpoint is called by a user with no tfa
    THEN expected_status is 200, both jwt access and refresh token
         in response and no tfa tokens was sent

    WHEN login endpoint is called by a user with tfa enabled and email device
    THEN expected_status is 202, only jwt access token in response and tfa tokens was sent

    WHEN login endpoint is called with data with tfa enabled and code gen device
    THEN expected_status is 202, only jwt access token in response and no tfa tokens was sent
    """
    # evaluate fixture
    mock_user = request.getfixturevalue(mock_user)
    # create mock user
    user = mock_user.create()

    response = await test_client.post(
        LOGIN_URL,
        data={
            'username': user.email,
            'password': mock_user.password
        }
    )
    assert response.status_code == expected_status
    assert (response.json().get('access_token') is not None) == expected_jwt_access_in_response
    assert (response.json().get('refresh_token') is not None) == expected_jwt_refresh_in_response

    assert mock_celery_send_mail.called == celery_sent_tfa_token


@pytest.mark.parametrize(
    "mock_user,expected_auth_call_response_status",
    [
        ('user_factory_no_tfa_factory', 200),
        ('user_with_email_device_factory', 403),
    ],
)
@pytest.mark.asyncio
async def test_login_session(
    mock_user,
    expected_auth_call_response_status,
    test_client,
    request,
    mock_celery_send_mail,
    async_session
):
    """
    GIVEN mock user model

    WHEN an authenticated endpoint is called by a user with no tfa
    THEN expected_status is 200

    WHEN an authenticated endpoint is called by a user with tfa
         enabled (needs yet to authenticate totp)
    THEN expected_status is 403
    """
    # evaluate fixture
    mock_user = request.getfixturevalue(mock_user)
    # create mock user
    user = mock_user.create()

    # login user
    response = await test_client.post(
        LOGIN_URL,
        data={
            'username': user.email,
            'password': mock_user.password
        }
    )
    # get access token and send in next request
    access_token = response.json()['access_token']

    response = await test_client.get(
        TEST_JWT_TOKEN,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == expected_auth_call_response_status
