from pydantic import BaseModel


class JwtTokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class JwtTokenPayload(BaseModel):
    sub: int = None
    exp: int = None


class PreTfaJwtTokenSchema(JwtTokenSchema):
    refresh_token: None
