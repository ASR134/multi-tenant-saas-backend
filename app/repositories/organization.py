from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.organization import Organization
from app.models.membership import Membership


class OrganizationRepository:

    def __init__(self,db : AsyncSession):
        self.db = db


    async def get_by_organization_id( # get specific organization by organization id 
            self,
            organization_id : int,
            user_id : int,
    ):
        result = await self.db.execute( # read db operation
            select(Organization)
            .join(Membership,Membership.organization_id == Organization.id)
            .where(
                Organization.id == organization_id,
                Membership.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()


    async def create(self,name : str) -> Organization:

        organization = Organization(
            name = name,
        )

        self.db.add(organization)

        await self.db.flush() # flush sends insert command (write db operation)

        return organization


    async def get_by_user_id(self,user_id : int): # get all organizations by user id

        result = await self.db.execute( # read db operation
            select(Organization)
            .join(Membership,Membership.organization_id == Organization.id)
            .where(Membership.user_id == user_id)
        )

        return result.scalars().all() # if no organizations return []

