from pydantic import SecretStr

from src.config.settings import Settings
from src.constants.enums import UserRole
from src.core.services.auth_service import AuthService


def test_google_admin_allowlist_promotes_matching_email() -> None:
    service = AuthService(
        session=None,  # type: ignore[arg-type]
        settings=Settings(
            jwt_secret_key=SecretStr("test-secret"),
            google_admin_emails=["admin@example.com"],
        ),
    )

    assert service._role_for_google_email("ADMIN@example.com") == UserRole.ADMIN


def test_google_admin_allowlist_defaults_to_worker() -> None:
    service = AuthService(
        session=None,  # type: ignore[arg-type]
        settings=Settings(jwt_secret_key=SecretStr("test-secret"), google_admin_emails=[]),
    )

    assert service._role_for_google_email("worker@example.com") == UserRole.WORKER

