from app.worker.tasks import send_invitation_accepted_notification

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership
from app.repositories.membership import MembershipRepository
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository

from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.utils.invitation import generate_invitation_token, hash_invitation_token, get_invitation_expiry
from app.services.email import EmailService


class InvitationService:

    def __init__(self,db : AsyncSession):
        self.db = db
        self.membership_repository = MembershipRepository(db)
        self.invitation_repository = InvitationRepository(db)
        self.email_service = EmailService()
        self.organization_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)


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

        invitation = await self.invitation_repository.get_by_org_id_and_email(# used to get invitation for given org_id and email
            organization_id=organization_id,
            email=email,
        )

        if invitation:

            if invitation.status == "accepted":
                raise ValueError("Invitee already member of organization")

            invitation_token = generate_invitation_token()
            invitation_token_hash = hash_invitation_token(invitation_token)
            invitation_token_expires_at = get_invitation_expiry()

            invitation.invitation_token_hash=invitation_token_hash
            invitation.invitation_token_expires_at=invitation_token_expires_at

            await self.db.flush()

            await self.db.commit()

            organization = await self.organization_repo.get_by_organization_id(
                organization_id=organization_id,
                user_id=user_id,
            )

            await self.email_service.send_invitation_email(
                email=email,
                invitation_token=invitation_token,
                organization_name=organization.name, # type: ignore
            )

            return invitation

        invitation_token = generate_invitation_token()
        invitation_token_hash = hash_invitation_token(invitation_token)
        invitation_token_expires_at = get_invitation_expiry()

        invitation = await self.invitation_repository.create( # write db operation
            organization_id=organization_id,
            email=email,
            invited_by=user_id,
            invitation_token_hash=invitation_token_hash,
            invitation_token_expires_at=invitation_token_expires_at,
        )

        await self.db.commit() 
        await self.db.refresh(invitation)

        organization = await self.organization_repo.get_by_organization_id(
            organization_id=organization_id,
            user_id=user_id,
        )
        
        await self.email_service.send_invitation_email(
            email=email,
            invitation_token=invitation_token,
            organization_name=organization.name, # type: ignore
        
        )
        return invitation


    async def accept_invitation( # after accepting invitation the token is invalidated
            self,
            invitation_token : str,
            user_id : int,
            user_email : str,
    ):
        invitation_token_hash = hash_invitation_token(invitation_token)

        # check whether invitation token is valid or not
        invitation = await self.invitation_repository.get_by_invitation_token_hash(
            invitation_token_hash = invitation_token_hash,
        )

        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Invalid invitation link",
            )

        # check whether is this the invited user
        if invitation.email != user_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This invitation was not sent to your email",
            )

        # check whether invitee already accepted - no need

        # check if invitation is expired or not
        if datetime.now(timezone.utc) > invitation.invitation_token_expires_at: # type: ignore
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

            await self.invitation_repository.update_status( # db operation 1
                invitation=invitation,
                status="accepted",
            )

            invitation.invitation_token_hash = None
            invitation.invitation_token_expires_at = None

            await self.db.commit()  # flush() is the write commmand for creating membership and invalidating invitation -> db operation 2
            # if all db operations are successful then only commit

        except Exception:
            await self.db.rollback() # uncommit all operations till the prev state of db
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Try again after few minutes",
            )

        inviter = await self.user_repo.get_by_id(
            user_id=invitation.invited_by,
        )

        organization = await self.organization_repo.get_by_organization_id(
            organization_id=invitation.organization_id,
            user_id=invitation.invited_by,
        )

        send_invitation_accepted_notification.delay( # celery puts this task into queue.
            inviter_email = inviter.email, # type: ignore
            invitee_email = invitation.email,
            organization_name = organization.name, # type: ignore
        )


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