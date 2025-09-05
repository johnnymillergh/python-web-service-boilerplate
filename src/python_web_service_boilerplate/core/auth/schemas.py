from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class UserRegistration(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    scopes: list[str] | None = None


class JWTPayload(BaseModel):
    # Subject (usually the username)
    sub: str
    # Expiration time
    eat: datetime
    # Scopes (permissions).
    scp: str

    def dump(self) -> dict[str, Any]:
        return {"sub": self.sub, "eat": self.eat.isoformat(), "scp": self.scp}


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
