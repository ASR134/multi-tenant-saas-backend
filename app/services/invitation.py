from app.worker.tasks import send_invitation_notification

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership
from app.repositories.membership import MembershipRepository
from app.repositories.invitation import InvitationRepository

import secrets
from datetime import datetime,timedelta,timezone

from fastapi import HTTPException, status


class InvitationService:

    def __init__(self,db : AsyncSession):
        self.db = db
        self.membership_repository = MembershipRepository(db)
        self.invitation_repository = InvitationRepository(db)


    async def create_invitation(
            self,
            organization_id : int,
            user_id : int,
            email : str,
    ):
        membership = await self.membership_repository.get_by_user_and_organization(
            organization_id=organization_id,
            user_id=user_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not member of this organization",
            )

        token = secrets.token_urlsafe(32)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        invitation = await self.invitation_repository.create( # write db operaion
            organization_id=organization_id,
            email=email,
            invited_by=user_id,
            token=token,
            expires_at=expires_at,
        )

        await self.db.commit() 
        await self.db.refresh(invitation)

        return invitation


    async def accept_invitation(
            self,
            token : str,
            user_id : int,
            user_email : str,
    ):
        
        # check whether invitation token is valid or not
        invitation = await self.invitation_repository.get_by_token(
            token = token,
        )

        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Invitation not found",
            )

        # check whether is this the invited user
        if invitation.email != user_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This invitation was not sent to your email",
            )

        # check whether invitee already accepted
        if invitation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = "Invitation is no longer pending",
            )

        # check if invitation is expired or not
        if datetime.now(timezone.utc) > invitation.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = "Invitation has expired",
            )
    
        # if this user is already member or not (for cases when email is send to a member already part of org)
        membership = await self.membership_repository.get_by_user_and_organization(
            user_id=user_id,
            organization_id=invitation.organization_id,
        )

        if membership is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = "You are already member of this organization",
            )

        try: # transaction
            membership = Membership( 
                user_id=user_id,
                organization_id =invitation.organization_id,
                role = "member",
            )

            self.db.add(membership)

            await self.invitation_repository.update_status( # db operation 2
                invitation=invitation,
                status="accepted",
            )

            await self.db.commit()  # flush() is the write commmand fro creating
            # if all db operations are successful then only commit

        except Exception:
            await self.db.rollback() # uncommit all operations till the prev state of db
            raise 
        
        await self.db.refresh(invitation)

        send_invitation_notification.delay(invitation.id)
        
        return invitation 


    async def get_invitations(
            self,
            organization_id :int,
            user_id : int,
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

        return await self.invitation_repository.get_by_organization(
            organization_id=organization_id,
        )