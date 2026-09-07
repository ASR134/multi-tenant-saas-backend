from app.repositories.membership import MembershipRepository
from sqlalchemy.ext.asyncio import AsyncSession


class MembershipServic:

    def __init__(self,db : AsyncSession):
        self.db = db
        self.membership_repository = MembershipRepository(db)

    async def get_membership(
            self,
            user_id : int,
            organization_id : int,
    ):
        return await self.membership_repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        )