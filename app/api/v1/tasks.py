from fastapi import APIRouter, status, Depends, Query

from app.schemas.task import TaskCreate,TaskResponse,TaskUpdate
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.task import TaskSerivce
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post(
    "/{organization_id}/{project_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    organization_id : int,
    project_id : int,
    task_data : TaskCreate,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):

    service = TaskSerivce(db)

    task = await service.create_task(
        organization_id=organization_id,
        project_id=project_id,
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
    )

    return task


@router.get(
    "/{organization_id}/{project_id}",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
)
async def get_tasks(
    organization_id : int,
    project_id : int,
    page : int = Query(1,ge=1), # query parameter for
    limit : int = Query(20,ge=1,le=100),# pagination
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):

    service = TaskSerivce(db)

    return await service.get_tasks_for_project(
        project_id=project_id,
        organization_id=organization_id,
        user_id=current_user.id,
        page = page,
        limit = limit,
    )


@router.get(
    "/{organization_id}/{project_id}/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    organization_id : int,
    project_id : int,
    task_id : int,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    service = TaskSerivce(db)

    return await service.get_task(
        organization_id=organization_id,
        user_id=current_user.id,
        project_id=project_id,
        task_id=task_id,
    )


@router.patch(
    "/{organization_id}/{project_id}/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    organization_id : int,
    project_id : int,
    task_id : int,
    task_data : TaskUpdate,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):

    service = TaskSerivce(db)

    return await service.update_task(
        organization_id=organization_id,
        project_id=project_id,
        task_id=task_id,
        user_id=current_user.id,
        title=task_data.title,
        curr_status=task_data.status,
        description=task_data.description,
        expected_version = task_data.version,
    )