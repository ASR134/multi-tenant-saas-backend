from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:


    def __init__(self,db : AsyncSession):
        self.db = db


    async def create(# create a project
        self,
        organization_id : int,
        name : str,
        description : str|None=None
    ):
        project = Project(
            organization_id = organization_id,
            name = name,
            description = description,
        )

        self.db.add(project)

        await self.db.flush() # write db operation (sends insert command)

        return project

    async def get_by_organization_id( # get projects by organization id
        self,
        organization_id : int,
        page : int,
        limit : int,
    ):

        offset = (page - 1)*limit

        result = await self.db.execute( # read db operation
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.id)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all() # gives a list of objects


    async def get_by_org_and_project_id(
            self,
            project_id : int,
            organization_id : int,
    ):
        project = await self.db.execute(
            select(Project).where(
                Project.organization_id == organization_id,
                Project.id == project_id,
            )
        )

        return project.scalar_one_or_none() # return project instance or None

    async def update(
            self,
            project : Project,
            expected_version : int,
            name : str | None=None, # it's update so can be None
            description : str | None = None,
    ):

        values : dict[str,object] = {
            "version" : project.version + 1
        }
        if name is not None:
            values["name"] = name

        if description is not None:
            values["description"] = description

        result = await self.db.execute( # for optimistic concurrency
            update(Project).where(
                Project.id == project.id,
                Project.version == expected_version,
            )
            .values(**values)
            .returning(Project)
        )

        return result.scalar_one_or_none()

    async def delete(
            self,
            project : Project,
    ):
        await self.db.delete(project)
        await self.db.flush() # forces delete command to run now