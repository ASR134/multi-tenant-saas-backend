from fastapi import APIRouter, status, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.db.session import get_db
from app.services.invitation import InvitationService
from app.dependencies.auth import get_current_user



router = APIRouter(
    prefix="/invitations",
    tags=["invitations"],
)


@router.post( 
    "/accept",
    response_model=InvitationResponse,
)
async def accept_invitation(
    token : str, # query parameter
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user),
):
    service = InvitationService(db)

    return await service.accept_invitation(
        token = token,
        user_id = current_user.id,
        user_email= current_user.email,
    )

# static routes first then dynamic routes in fastapi
@router.post(
    "/{organization_id}",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    organization_id : int,
    invitation_data : InvitationCreate,
    currect_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):

    service = InvitationService(db)

    return await service.create_invitation(
        organization_id=organization_id,
        user_id=currect_user.id,
        email=invitation_data.email,
    )


@router.get(
    "/{organization_id}",
    response_model=list[InvitationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_invitations(
    organization_id : int,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    service = InvitationService(db)

    return await service.get_invitations(
        organization_id=organization_id,
        user_id=current_user.id,
    )