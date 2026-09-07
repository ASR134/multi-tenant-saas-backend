from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership


class MembershipRepository:

    def __init__(self,db: AsyncSession):
        self.db = db


    async def get_by_user_and_organization(
            self,
            user_id : int,
            organization_id : int,
    ):
        result = await self.db.execute( # read db operation
            select(Membership).where(
                Membership.organization_id == organization_id,
                Membership.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()