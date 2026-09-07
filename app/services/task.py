from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from app.repositories.task import TaskRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository


class TaskSerivce:

    def __init__(self,db : AsyncSession):
        self.db = db
        self.task_repository = TaskRepository(db)
        self.membership_repository = MembershipRepository(db)
        self.project_repository = ProjectRepository(db)


    async def create_task(
            self,
            organization_id : int,
            project_id : int,
            user_id : int,
            title : str,
            description : str|None = None,
    ):
        # check that user belongs to org or not

        membership =await self.membership_repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail = "You are not member of this organization",
            )

        # check that project belongs to org or not

        project =await self.project_repository.get_by_org_and_project_id(
            project_id=project_id,
            organization_id=organization_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # create task

        task = await self.task_repository.create(# write db op
            project_id=project_id,
            title=title,
            description=description,
        )

        await self.db.commit()
        await self.db.refresh(task)

        return task


    async def get_tasks_for_project(
            self,
            project_id : int,
            organization_id : int,
            user_id : int,
            page : int,
            limit : int,
    ):

        # check that user belongs to org or not
        
        membership =await self.membership_repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        )
        
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail = "You are not member of this organization",
            )

        # check that project belongs to org or not
        
        project =await self.project_repository.get_by_org_and_project_id(
            project_id=project_id,
            organization_id=organization_id,
        )
        
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        tasks = await self.task_repository.get_all_for_project(
            project_id=project_id,
            page = page,
            limit = limit,
        )

        return tasks


    async def get_task(
                self,
                organization_id : int,
                user_id : int,
                project_id : int,
                task_id : int,
    ):
        membership =await self.membership_repository.get_by_user_and_organization(
                        user_id=user_id,
                        organization_id=organization_id,
                    )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail = "You are not member of this organization"
            )

        project =await self.project_repository.get_by_org_and_project_id(
                    project_id=project_id,
                    organization_id=organization_id,
                )
                
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        task = await self.task_repository.get_by_project_and_task_id(
            project_id=project_id,
            task_id=task_id,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Task not found",
            )

        return task


    async def update_task(
            self,
            organization_id : int,
            project_id : int,
            task_id : int,
            user_id : int,
            expected_version : int,
            title : str | None = None,
            description : str | None = None,
            curr_status : str| None = None,
    ):

        membership =await self.membership_repository.get_by_user_and_organization(
                        user_id=user_id,
                        organization_id=organization_id,
                    )
        
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail = "You are not member of this organization"
            )
        
        project =await self.project_repository.get_by_org_and_project_id(
                    project_id=project_id,
                    organization_id=organization_id,
                )
                        
        if project is None:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )
        
        task = await self.task_repository.get_by_project_and_task_id(
                project_id=project_id,
                task_id=task_id,
            )
        
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Task not found",
            )

        task = await self.task_repository.update(# write db operation
            task =task,
            title=title,
            status=curr_status,
            description=description,
            expected_version = expected_version,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail = "Task was modified by another user",
            )
        
        await self.db.commit()

        return task