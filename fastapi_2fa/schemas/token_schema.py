from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: int = None
    exp: int = None


class PreTfaTokenSchema(TokenSchema):
    refresh_token: None
