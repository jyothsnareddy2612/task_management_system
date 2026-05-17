from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from src.config.settings import Settings, get_settings
from src.core.exceptions import AuthenticationError


def hash_password(password: str) -> str:
    password_digest = hashlib.sha256(password.encode("utf-8")).digest()
    return bcrypt.hashpw(password_digest, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    password_digest = hashlib.sha256(password.encode("utf-8")).digest()
    return bcrypt.checkpw(password_digest, hashed_password.encode("utf-8"))


def create_token(
    *,
    subject: UUID,
    role: str,
    token_type: str,
    expires_delta: timedelta,
    settings: Settings | None = None,
) -> str:
    active_settings = settings or get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(
        payload,
        active_settings.jwt_secret_key.get_secret_value(),
        algorithm=active_settings.jwt_algorithm,
    )


def decode_token(token: str, expected_type: str, settings: Settings | None = None) -> dict[str, Any]:
    active_settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            active_settings.jwt_secret_key.get_secret_value(),
            algorithms=[active_settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        raise AuthenticationError("Invalid token type")
    return payload
