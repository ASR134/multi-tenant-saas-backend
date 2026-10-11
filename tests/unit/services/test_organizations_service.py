from types import SimpleNamespace 
from unittest.mock import AsyncMock, MagicMock, call

import pytest
from fastapi import HTTPException

from app.services.organization import OrganizationService
from app.models.membership import Membership

@pytest.fixture
def db():

    session = MagicMock()# object provides method so magicmock is sensible default.

    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    return session


@pytest.fixture
def repository():# mock organization repository object
    repo = MagicMock() # object provides method so magicmock is sensible default.

    repo.create = AsyncMock()
    repo.get_by_organization_id = AsyncMock()
    repo.get_by_user_id = AsyncMock()

    return repo


@pytest.fixture
def service(db, repository, monkeypatch):# inject the mocked repo into the sevice
    monkeypatch.setattr(
        "app.services.organization.OrganizationRepository",
        lambda db : repository, # this means take db as input 
    )

    return OrganizationService(db) # fake db object passed. now python will execute OrganizationService(db)


#--------------------------------------------------------------------------------------------------------------------
# create_organization()
@pytest.mark.asyncio
async def test_create_organization_success(
    db,
    repository,
    service,
):
    organization = SimpleNamespace(
        id = 10,
        name = "Test Organization",
    )

    repository.create.return_value = organization # need to initialise before actual service method is called

    result = await service.create_organization( # executes the service method
        name = "Test Organization",
        user_id = 1,
    )

    # assert organization creation
    repository.create.assert_awaited_once_with(
        name = "Test Organization",
    )

    # assert Owner membership creation
    db.add.assert_called_once()
    membership = db.add.call_args.args[0] # call_args.args contains positional arg

    assert isinstance(membership,Membership)
    assert membership.user_id == 1
    assert membership.organization_id == 10
    assert membership.role == "owner"

    # transaction and refresh
    db.commit.assert_awaited_once_with()
    db.refresh.assert_awaited_once_with(organization)
    db.rollback.assert_not_awaited()

    assert result is organization


@pytest.mark.asyncio
async def test_create_organization_rolls_back_on_repository_failure(
    db,
    repository,
    service,
):
    # arrange 
    repository.create.side_effect = RuntimeError("Database Error")

    # act and assert
    with pytest.raises(RuntimeError, match="Database Error"): # tell pytest to expect the exception
        await service.create_organization(
            name="Test Organization",
            user_id=1,
        )

    # assert
    db.rollback.assert_awaited_once()
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_organization_rolls_back_on_commit_failure(
    db,
    repository,
    service,
):
    # arrange
    organization = SimpleNamespace(
        id = 10,
        name = "Test Organization",
    )
    repository.create.return_value = organization
    db.commit.side_effect = RuntimeError("Commit failed")

    # act and assert
    with pytest.raises(RuntimeError,match="Commit failed"):
        await service.create_organization(
            name = "Test Organization",
            user_id=1,
        )

    # assert
    db.commit.assert_awaited_once()
    db.rollback.assert_awaited_once()
    db.refresh.assert_not_awaited()

#------------------------------------------------------------------------------------------------------------------
# get_organization_by_org_id()
@pytest.mark.asyncio
async def test_get_organization_by_org_id_success(
    repository,
    service,
):
    # arrange 
    organization = SimpleNamespace(
        id = 10,
        name = "Test Organization",
    )

    repository.get_by_organization_id.return_value = organization

    # act
    result = await service.get_organization_by_org_id( # service method called
        organization_id=10,
        user_id=1,
    )

    #assert
    repository.get_by_organization_id.assert_awaited_once_with(
        organization_id = 10,
        user_id = 1,
    )

    assert result is organization



@pytest.mark.asyncio
async def test_get_organization_by_org_id_not_found(
    repository,
    service,
):
    # arrange
    repository.get_by_organization_id.return_value = None

    # act and assert
    with pytest.raises(HTTPException) as exc_info: # tells pytest to expect this exception
        await service.get_organization_by_org_id( # service method called
            organization_id=10,
            user_id=1,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Organization not found"