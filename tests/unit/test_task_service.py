from uuid import uuid4

import pytest

from src.constants.enums import UserRole
from src.core.exceptions import PermissionDeniedError
from src.core.services.task_service import TaskService


class DummyUser:
    id = uuid4()
    role = UserRole.WORKER


def test_worker_cannot_use_admin_operation() -> None:
    service = TaskService(session=None, notifications=None)  # type: ignore[arg-type]
    with pytest.raises(PermissionDeniedError):
        service._require_admin(DummyUser())  # type: ignore[arg-type]

