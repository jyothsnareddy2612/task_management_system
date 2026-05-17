from uuid import uuid4

import pytest

from src.constants.enums import TaskStatus, UserRole
from src.core.exceptions import PermissionDeniedError
from src.core.services.task_service import TaskService


class DummyUser:
    id = uuid4()
    role = UserRole.WORKER


def build_service() -> TaskService:
    return TaskService(session=None, notifications=None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("old_status", "new_status"),
    [
        (TaskStatus.TODO, TaskStatus.TODO),
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS),
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.DONE),
    ],
)
def test_allowed_status_transitions(old_status: TaskStatus, new_status: TaskStatus) -> None:
    build_service()._validate_status_transition(old_status, new_status)


@pytest.mark.parametrize(
    ("old_status", "new_status"),
    [
        (TaskStatus.TODO, TaskStatus.DONE),
        (TaskStatus.IN_PROGRESS, TaskStatus.TODO),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
        (TaskStatus.DONE, TaskStatus.TODO),
    ],
)
def test_invalid_status_transitions(old_status: TaskStatus, new_status: TaskStatus) -> None:
    with pytest.raises(PermissionDeniedError):
        build_service()._validate_status_transition(old_status, new_status)

