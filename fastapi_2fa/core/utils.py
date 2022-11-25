from dataclasses import dataclass

from pydantic import EmailStr

from fastapi_2fa.core.config import settings
from fastapi_2fa.models.device import Device
from fastapi_2fa.models.users import User
from fastapi_2fa.tasks.tasks import send_email


@dataclass(slots=True, frozen=True)
class Email:
    to_: list[EmailStr]
    from_: EmailStr
    text_: str

    def __repr__(self) -> str:
        return (
            f"Email (to: {self.to_}), "
            f"(from: {self.from_}), "
            f"(text: {self.text_})"
        )


def send_backup_tokens(user: User, device: Device):
    email_ob = Email(
        to_=[user.email],
        from_=settings.FAKE_EMAIL_SENDER,
        text_=f"Backup tokens : {device.backup_tokens}"
    )
    send_email(email=email_ob)


def send_totp_token(user: User, token: str):
    email_ob = Email(
        to_=[user.email],
        from_=settings.FAKE_EMAIL_SENDER,
        text_=f"Access TOTP token : {token}"
    )
    send_email(email=email_ob)
