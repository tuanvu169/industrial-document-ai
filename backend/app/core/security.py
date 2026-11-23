import uuid
from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    email: str | None


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    """Verify the Supabase access token by asking Supabase Auth who it belongs to."""
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Thiếu access token")
    try:
        resp = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={"apikey": settings.supabase_anon_key, "Authorization": f"Bearer {creds.credentials}"},
            timeout=10,
        )
    except httpx.HTTPError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Không kết nối được Supabase Auth")
    if resp.status_code != 200:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Access token không hợp lệ hoặc đã hết hạn")
    data = resp.json()
    return CurrentUser(id=uuid.UUID(data["id"]), email=data.get("email"))
