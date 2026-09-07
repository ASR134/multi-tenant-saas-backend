from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException,status

from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.repositories.comment import CommentRepository


class CommentService:

    def __init__(self,db : AsyncSession):
        self.db = db

        self.membership_repository = MembershipRepository(db)
        self.comment_repository = CommentRepository(db)
        self.project_repository = ProjectRepository(db)
        self.task_repository = TaskRepository(db)


    async def create_comment(
            self,
            organization_id : int,
            user_id : int,
            project_id : int,
            task_id : int,
            content : str,
    ):

        # check membership
        membership = await self.membership_repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the member of this organization",
            )

        # check project belonginess to org

        project = await self.project_repository.get_by_org_and_project_id(
            organization_id=organization_id,
            project_id=project_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Project not found",
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

        comment = await self.comment_repository.create( # write db operation
            content=content,
            user_id=user_id,
            task_id=task_id,
        )

        await self.db.commit()

        return comment


    async def get_comments(
            self,
            organization_id : int,
            user_id : int,
            project_id : int,
            task_id : int,
            page : int,
            limit : int,
    ):
        # check membership
        membership = await self.membership_repository.get_by_user_and_organization(
                        user_id=user_id,
                        organization_id=organization_id,
                    )
        
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the member of this organization",
            )
        
        # check project belonginess to org
        
        project = await self.project_repository.get_by_org_and_project_id(
                    organization_id=organization_id,
                    project_id=project_id,
                )
        
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Project not found",
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

        comments = await self.comment_repository.get_by_task_id(
            task_id=task_id,
            page = page,
            limit = limit,
        )

        return comments


    async def get_comment(
        self,
        organization_id: int,
        project_id: int,
        task_id: int,
        comment_id: int,
        user_id: int,
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

        project = await self.project_repository.get_by_org_and_project_id(
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
                detail="Task not found",
            )

        comment = await self.comment_repository.get_by_task_and_comment_id(
            task_id=task_id,
            comment_id=comment_id,
        )

        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        return comment


    async def delete_comment(
            self,
            organization_id:int,
            user_id:int,
            project_id : int,
            task_id : int,
            comment_id : int,
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

        project = await self.project_repository.get_by_org_and_project_id(
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
                detail="Task not found",
            )

        comment = await self.comment_repository.get_by_task_and_comment_id(
            task_id=task_id,
            comment_id=comment_id,
        )

        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        await self.comment_repository.delete(comment) # write db operation

        await self.db.commit()