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
            invitation_token_hash : str,
            invitation_token_expires_at : datetime,
    ):
        invitation = Invitation(
            organization_id=organization_id,
            email = email,
            invitation_token_hash = invitation_token_hash ,
            invited_by = invited_by,
            invitation_token_expires_at= invitation_token_expires_at,
        )

        self.db.add(invitation)

        await self.db.flush() # write db operation (sends insert command)

        return invitation


    async def get_by_invitation_token_hash( # gives unique invitation if valid token
            self,
            invitation_token_hash : str,
    ):

        result = await self.db.execute(select(Invitation).where(
            Invitation.invitation_token_hash == invitation_token_hash,
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


    async def get_by_org_id_and_email( # used to get any invitation (whther pending or accepted) for given org_id and email.
            self,
            organization_id : int,
            email : str,
    ):

        invitation = await self.db.execute(select(Invitation).where(
            Invitation.organization_id == organization_id,
            Invitation.email == email,
        ))

        return invitation.scalar_one_or_none()


    async def update_status(
            self,
            invitation : Invitation,
            status : str,
    ):
        invitation.status = status # explicitly changed the value for py obj so refresh not necessay in service 

        await self.db.flush() # write (update) db operation (sends update command)

        return invitation