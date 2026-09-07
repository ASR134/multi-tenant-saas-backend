from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update

from app.models.task import Task


class TaskRepository:

    def __init__(self,db : AsyncSession):
        self.db = db


    async def create(
            self,
            project_id : int,
            title : str,
            description : str | None = None,
    ):

        task = Task(project_id=project_id,
                    title=title,
                    description=description
                )

        self.db.add(task)

        await self.db.flush()

        return task


    async def get_by_project_and_task_id(
            self,
            project_id : int,
            task_id : int,
    ):
        result = await self.db.execute(
                select(Task).where(
                Task.id == task_id,
                Task.project_id == project_id,
            )
        )

        return result.scalar_one_or_none()


    async def get_all_for_project(
            self,
            project_id : int,
            page : int,
            limit : int,
    ):
        offset = (page - 1) * limit

        result = await self.db.execute(
            select(Task).where(
                Task.project_id == project_id,
            )
            .order_by(Task.id)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()


    async def update(
            self,
            task : Task,
            expected_version : int,
            title : str|None=None,
            description : str|None = None,
            status : str|None=None,
    ):
        values: dict[str, object] = {
            "version":Task.version + 1,
        }

        if title is not None:
            values["title"] = title

        if description is not None:
            values["description"] = description

        if status is not None:
            values["status"] = status

        result = await self.db.execute(
            update(Task)
            .where(
                Task.id == task.id,
                Task.version == expected_version,
            )
            .values(**values)
            .returning(Task)
        )

        return result.scalar_one_or_none()

