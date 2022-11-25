from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str | None


class TokenPayload(BaseModel):
    sub: int = None
    exp: int = None


class PreTfaTokenSchema(BaseModel):
    pre_tfa_token: str
