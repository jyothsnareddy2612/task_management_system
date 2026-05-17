from datetime import timedelta
from uuid import uuid4

from src.utils.security import create_token, decode_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    hashed = hash_password("strong-password")
    assert verify_password("strong-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_round_trip() -> None:
    user_id = uuid4()
    token = create_token(
        subject=user_id,
        role="ADMIN",
        token_type="access",
        expires_delta=timedelta(minutes=5),
    )
    payload = decode_token(token, "access")
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "ADMIN"

