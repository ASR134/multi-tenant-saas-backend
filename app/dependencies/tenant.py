from fastapi import HTTPException, status,Depends

from app.db.session import get_db
from app.services.organization import OrganizationService
from app.models.user import User
from app.dependencies.auth import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_organization( # gives the org of current user
        organization_id : int,
        current_user : User =Depends(get_current_user),
        db : AsyncSession = Depends(get_db),
):

    service = OrganizationService(db)

    organization = await service.get_organization_by_org_id(
        organization_id=organization_id,
        user_id=current_user.id,
    )

    return organization