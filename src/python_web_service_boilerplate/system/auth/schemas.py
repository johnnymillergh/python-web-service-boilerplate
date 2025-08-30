from datetime import datetime

from pydantic import BaseModel


class UserRegistration(BaseModel):
    username: str
    password: str
    email: str
    full_name: str


class JWTPayload(BaseModel):
    sub: str  # Subject (usually the username)
    expires_at: datetime  # Expiration time

    def dump(self) -> dict[str, str]:
        return {"sub": self.sub, "expires_at": self.expires_at.isoformat()}


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
