import json
from dataclasses import asdict, dataclass

from celery.result import AsyncResult
from pydantic import EmailStr

from fastapi_2fa.core.config import settings
from fastapi_2fa.models.device import Device
from fastapi_2fa.models.users import User
from fastapi_2fa.tasks.tasks import send_email_task


@dataclass(slots=True, frozen=True)
class Email:
    to_: list[EmailStr]
    from_: EmailStr
    text_: str

    def to_json(self):
        """
        get the json formated string
        """
        return json.dumps(asdict(self))

    def __repr__(self) -> str:
        return (
            f"Email (to: {self.to_}), "
            f"(from: {self.from_}), "
            f"(text: {self.text_})"
        )


def send_mail_backup_tokens(user: User, device: Device) -> AsyncResult:
    email_obj = Email(
        to_=[user.email],
        from_=settings.FAKE_EMAIL_SENDER,
        text_=f"Backup tokens : {device.backup_tokens}"
    )
    print(
        f"Sending email task to celery, email:\n\n***\n{email_obj.text_}\n***\n"
    )
    task = send_email_task.apply_async(kwargs={'email': email_obj.to_json()})
    return task


def send_mail_totp_token(user: User, token: str) -> AsyncResult:
    email_obj = Email(
        to_=[user.email],
        from_=settings.FAKE_EMAIL_SENDER,
        text_=f"Access TOTP token : {token}"
    )
    print(
        f"Sending email task to celery, email:\n\n***\n{email_obj.text_}\n***\n"
    )
    task = send_email_task.apply_async(kwargs={'email': email_obj.to_json()})
    return task
