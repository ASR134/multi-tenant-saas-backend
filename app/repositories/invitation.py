from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invitation import Invitation

from datetime import datetime


class InvitationRepository:

    def __init__(self,db : AsyncSession):
        self.db = db


    async def create(
            self,
            organization_id : int,
            email : str,
            invited_by : int,
            token : str,
            expires_at : datetime,
    ):
        invitation = Invitation(
            organization_id=organization_id,
            email = email,
            token = token,
            invited_by = invited_by,
            expires_at = expires_at,
        )

        self.db.add(invitation)

        await self.db.flush() # write db operation (sends insert command)

        return invitation


    async def get_by_token( # gives unique invitation if valid token
            self,
            token : str,
    ):

        result = await self.db.execute(select(Invitation).where(
            Invitation.token == token,
        ))

        return result.scalar_one_or_none()


    async def get_by_organization(
            self,
            organization_id : int,
    ):
        result = await self.db.execute(select(Invitation).where(
            Invitation.organization_id == organization_id,
        ).order_by(Invitation.id))

        return result.scalars().all()


    async def update_status(
            self,
            invitation : Invitation,
            status : str,
    ):
        invitation.status = status # explicitly changed the value for py obj so refresh not necessay in service 

        await self.db.flush() # write (update) db operation (sends update command)

        return invitation