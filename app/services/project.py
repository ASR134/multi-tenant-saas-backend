from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.repositories.membership import MembershipRepository

import json
from app.db.redis import redis_client

class ProjectService:

    def __init__(self,db:AsyncSession):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.membership_repository = MembershipRepository(db)


    async def create_project(
            self,
            organization_id : int,
            name : str,
            user_id : int,
            description : str|None=None,
    ):

        memebership = await self.membership_repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        ) # a user can only create a project inside an org they belong to.
        # read db operation
        if memebership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not member of this organization",
            )

        project = await self.project_repository.create( # write db op
            organization_id=organization_id,
            name=name,
            description=description,
        )

        await self.db.commit()
        await self.db.refresh(project)

        cache_pattern = f"projects:org:{organization_id}:page:*"

        keys = await redis_client.keys(cache_pattern) # returns list of keys
        if keys:
            await redis_client.delete(*keys) # removes cached project list for this org

        return project


    async def get_projects_for_organization(
            self,
            organization_id : int,
            user_id : int,
            page : int,
            limit : int,
    ):
        membership = await self.membership_repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        )

        if membership is None:
            raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You are not member of this organization",
                    )

        cache_key = f"projects:org:{organization_id}:page:{page}:limit:{limit}"

        cached_projects = await redis_client.get(cache_key)

        if cached_projects:
            return json.loads(cached_projects)

        projects = await self.project_repository.get_by_organization_id(
            organization_id=organization_id,
            page = page,
            limit = limit,
        )

        projects_data = [
            {
                "id" : project.id,
                "organization_id" : project.organization_id,
                "name" : project.name,
                "description" : project.description,
                "created_at" : project.created_at.isoformat(),
                "version" : project.version,
            }
            for project in projects
        ]

        await redis_client.set(
            cache_key,
            json.dumps(projects_data), # converts py obj to json
            ex=60, # this cached data expires after 60sec
        )

        return projects


    async def get_project_with_org_and_project_id(
            self,
            organization_id : int,
            project_id : int,
            user_id : int,
    ):
        membership = await self.membership_repository.get_by_user_and_organization(
                    user_id=user_id,
                    organization_id=organization_id,
                )
        
        if membership is None:
            raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not member of this organization",
            )

        cache_key = f"project:org:{organization_id}:id:{project_id}"

        cashed_project = await redis_client.get(cache_key)

        if cashed_project:
            return json.loads(cashed_project)

        project = await self.project_repository.get_by_org_and_project_id(
            organization_id=organization_id,
            project_id=project_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        project_data = {
            "id" : project.id,
            "name" : project.name,
            "organization_id" : project.organization_id,
            "description" : project.description,
            "created_at" : project.created_at.isoformat(),
            "version" : project.version,
        }

        await redis_client.set(
            cache_key,
            json.dumps(project_data),
            ex=60,
        )

        return project


    async def update_project(
            self,
            organization_id:int,
            user_id : int,
            expected_version : int,
            project_id : int,
            name : str | None = None,
            description : str | None=None
    ):
        membership = await self.membership_repository.get_by_user_and_organization(
                            user_id=user_id,
                            organization_id=organization_id,
                        ) # read db operation
                
        if membership is None:# user can only update a project of an org he/she belongs to.
            raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not member of this organization",
                )

        project = await self.project_repository.get_by_org_and_project_id(
                    organization_id=organization_id,
                    project_id=project_id,
                )# read db op
        
        if project is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )

        project = await self.project_repository.update( # write db op
            project=project,
            name=name,
            description=description,
            expected_version = expected_version,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project was modified by another user",
            )
        
        await self.db.commit()
        
        # cashe pattern for single project
        cashe_key = f"project:org:{organization_id}:id:{project_id}"
        await redis_client.delete(cashe_key)

        # cache pattern for list of projects
        cache_pattern = f"projects:org:{organization_id}:page:*"
        keys = await redis_client.keys(cache_pattern) # returns list of keys
        
        if keys: # if req for dynamically generated keys -> could be zero that's why
            await redis_client.delete(*keys)

        return project


    async def delete_project(
            self,
            organization_id : int,
            project_id : int,
            user_id : int,
    ):
        membership = await self.membership_repository.get_by_user_and_organization(
                                    user_id=user_id,
                                    organization_id=organization_id,
                                )
                        
        if membership is None:# user can only delete a project of an org he/she belongs to.
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not member of this organization",
                )

        project = await self.project_repository.get_by_org_and_project_id(
            project_id=project_id,
            organization_id=organization_id,
        )

        if project is None:
            raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project not found",
                    )

        await self.project_repository.delete(project=project) # write db op

        await self.db.commit()

        # invalidating cached single project
        cache_key = f"project:org:{organization_id}:id:{project_id}"
        await redis_client.delete(cache_key)

        # invalidating list of projects
        cache_pattern = f"projects:org:{organization_id}:page:*"
        keys = await redis_client.keys(cache_pattern)

        if keys:
            await redis_client.delete(*keys)