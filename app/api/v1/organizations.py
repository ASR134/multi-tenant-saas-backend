from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.tenant import get_current_organization
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.db.session import get_db
from app.services.organization import OrganizationService

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    organization_data : OrganizationCreate,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)

    organization = await service.create_organization(
        name = organization_data.name,
        user_id = current_user.id,
    )

    return organization

# get all the organiztions user belongs to -> uses user_id
@router.get(
    "",
    response_model=list[OrganizationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_organizations(
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)

    organizations = await service.get_organizations_by_user_id(
        user_id=current_user.id,
    )

    return organizations


# get the specific organization user belongs to by org_id  -> use user_id and org_id
@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
async def get_organization_by_org_id(
    organization : Organization = Depends(get_current_organization),
):
    return organization