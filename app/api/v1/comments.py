from fastapi import APIRouter,status,Depends, Query

from app.db.session import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User
from app.services.comment import CommentService
from app.schemas.comment import CommentCreate,CommentResponse

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.post(
    "/{organization_id}/{project_id}/{task_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    organization_id : int,
    project_id : int,
    task_id : int,
    comment_data : CommentCreate,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):
    service = CommentService(db)

    return await service.create_comment(
        organization_id=organization_id,
        user_id=current_user.id,
        project_id=project_id,
        task_id=task_id,
        content=comment_data.content,
    )


@router.get(
    "/{organization_id}/{project_id}/{task_id}",
    response_model=list[CommentResponse],
)
async def get_commments(
    organization_id : int,
    project_id :int,
    task_id : int,
    page : int = Query(1,ge=1),
    limit : int = Query(20,ge=20,le=100),
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):

    service = CommentService(db)

    return await service.get_comments(
        organization_id=organization_id,
        user_id = current_user.id,
        project_id=project_id,
        task_id=task_id,
        page = page,
        limit = limit,
    )


@router.get(
    "/{organization_id}/{project_id}/{task_id}/{comment_id}",
    response_model=CommentResponse,
)
async def get_commment(
    organization_id : int,
    project_id :int,
    task_id : int,
    comment_id :int,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):

    service = CommentService(db)

    return await service.get_comment(
        organization_id=organization_id,
        comment_id=comment_id,
        user_id = current_user.id,
        project_id=project_id,
        task_id=task_id,
    )


@router.delete(
    "/{organization_id}/{project_id}/{task_id}/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_commment(
    organization_id : int,
    project_id :int,
    task_id : int,
    comment_id :int,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):

    service = CommentService(db)

    return await service.delete_comment(
        organization_id=organization_id,
        comment_id=comment_id,
        user_id = current_user.id,
        project_id=project_id,
        task_id=task_id,
    )