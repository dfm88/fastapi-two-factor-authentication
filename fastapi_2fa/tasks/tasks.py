import typing
from time import sleep

if typing.TYPE_CHECKING:
    from fastapi_2fa.core.utils import Email


def send_email(email: 'Email'):
    print('Sending email..')
    sleep(2)
    print('\nEmail sent:\n')
    print(email)
