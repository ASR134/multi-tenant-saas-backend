from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.project import ProjectCreate, ProjectResponse,ProjectUpdate
from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.project import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/{organization_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    organization_id : int,
    project_data : ProjectCreate,
    db : AsyncSession = Depends(get_db),
    currect_user : User = Depends(get_current_user)
):
    service = ProjectService(db)

    project = await service.create_project(
        organization_id=organization_id,
        name=project_data.name,
        user_id=currect_user.id,
        description=project_data.description,
    )

    return project


@router.get(
    "/{organization_id}",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK
)
async def get_projects_by_org_id(
    organization_id : int,
    page : int = Query(1,ge=1),
    limit : int = Query(20,ge=1,le=100), 
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    projects = await service.get_projects_for_organization(
        organization_id=organization_id,
        user_id=current_user.id,
        page = page,
        limit = limit,
    )

    return projects


@router.get(
    "/{organization_id}/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project_by_org_and_project_id(
    organization_id : int,
    project_id :int,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    project = await service.get_project_with_org_and_project_id(
        organization_id=organization_id,
        project_id=project_id,
        user_id=current_user.id,
    )

    return project


@router.patch( # patch -> see ProjectUpdate schema
    "/{organization_id}/{project_id}",
    response_model=ProjectUpdate,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    organization_id : int,
    project_id : int,
    project_data : ProjectUpdate,
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user), # non default/required args then default/dependency args
):
    service = ProjectService(db)

    return await service.update_project(
        organization_id=organization_id,
        user_id=current_user.id,
        project_id=project_id,
        name=project_data.name,
        description=project_data.description,
        expected_version = project_data.version,
    )


@router.delete(
    "/{organization_id}/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    organization_id : int,
    project_id : int,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    await service.delete_project(
        organization_id=organization_id,
        project_id=project_id,
        user_id=current_user.id,
    )