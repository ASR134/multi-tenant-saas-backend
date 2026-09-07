from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status

from app.repositories.organization import OrganizationRepository

from app.models.membership import Membership

class OrganizationService:

    def __init__(self,db : AsyncSession):
        self.db = db
        self.organization_repository = OrganizationRepository(db)


    async def create_organization(
            self,
            name : str,
            user_id : int,
    ):
        try:
            organization = await self.organization_repository.create(
                name = name, # write db operation
            )

            membership = Membership( # creating organization automatically creates membership
                user_id = user_id,
                organization_id = organization.id,
                role = "owner",
            )

            self.db.add(membership)
            # write db operation (flush)
            await self.db.commit() # auto flushes

        except Exception:
            await self.db.rollback()
            raise

        await self.db.refresh(organization)
        # we don't require membership sync right now so no refresh.
        return organization


    async def get_organization_by_org_id(
            self,
            organization_id : int,
            user_id : int,
    ):
        organization = await self.organization_repository.get_by_organization_id(
            organization_id=organization_id,
            user_id=user_id,
        )

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not member of this organization",
            )


        return organization


    async def get_organizations_by_user_id(
            self,
            user_id : int,
    ):
        return await self.organization_repository.get_by_user_id(
            user_id=user_id,
        )