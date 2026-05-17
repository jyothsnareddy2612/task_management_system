from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.rest.dependencies import get_comment_service, get_current_user
from src.core.services.comment_service import CommentService
from src.data.models.postgres.comment import Comment
from src.data.models.postgres.user import User
from src.schemas.comments import CommentCreate, CommentRead

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def add_comment(
    task_id: UUID,
    payload: CommentCreate,
    actor: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
) -> Comment:
    return await service.add(task_id, payload, actor)


@router.get("", response_model=list[CommentRead])
async def list_comments(
    task_id: UUID,
    actor: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
) -> list[Comment]:
    return await service.list_for_task(task_id, actor)

