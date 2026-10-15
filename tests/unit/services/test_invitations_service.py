from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from app.services.invitation import InvitationService

# these fixtures are responsible for creating and returning mock objects
@pytest.fixture
def db():
    session = MagicMock()

    session.commit = AsyncMock()
    session.add = MagicMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()

    return session


@pytest.fixture
def membership_repository():
    repo = MagicMock()

    repo.get_by_user_and_organization = AsyncMock()

    return repo


@pytest.fixture
def invitation_repository():
    repo = MagicMock()

    repo.get_by_org_id_and_email = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_invitation_token_hash = AsyncMock()
    repo.update_status = AsyncMock()
    repo.get_by_organization = AsyncMock()

    return repo


@pytest.fixture
def organization_repository():
    repo = MagicMock()

    repo.get_by_organization_id = AsyncMock()

    return repo


@pytest.fixture
def user_repository():
    repo = MagicMock()

    repo.get_by_id = AsyncMock()

    return repo


@pytest.fixture(name="email_service")
def email_service():
    email = MagicMock()

    email.send_invitation_email = AsyncMock()

    return email


@pytest.fixture
def service(
    db,
    membership_repository,
    organization_repository,
    invitation_repository,
    user_repository,
    email_service,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.invitation.MembershipRepository",
        lambda db: membership_repository,
    )

    monkeypatch.setattr(
        "app.services.invitation.InvitationRepository",
        lambda db: invitation_repository,
    )

    monkeypatch.setattr(
        "app.services.invitation.OrganizationRepository",
        lambda db: organization_repository,
    )

    monkeypatch.setattr(
        "app.services.invitation.UserRepository",
        lambda db: user_repository,
    )

    monkeypatch.setattr(
        "app.services.invitation.EmailService",
        lambda : email_service,
    )
    # monkeypatch + lambda -> replaces the function with a predictable return value.
    # MagicMock(return_value = ..) -> replaces the function with a mock that also lets us to assert how it was called but for that store the mock in a variable. 
    monkeypatch.setattr(
        "app.services.invitation.generate_invitation_token",
        lambda : "test-token", # now this function will return test-token
    )

    monkeypatch.setattr(
        "app.services.invitation.hash_invitation_token",
        lambda token : "hashed-test-token",
    )

    monkeypatch.setattr(
        "app.services.invitation.get_invitation_expiry",
        lambda : datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    monkeypatch.setattr(
        "app.services.invitation.send_invitation_accepted_notification",
        MagicMock(),
    )

    return InvitationService(db)

#--------------------------------
# create_invitation()
@pytest.mark.asyncio
async def test_create_invitation_success(
    db,
    membership_repository,
    invitation_repository,
    organization_repository,
    email_service,
    service,
):
    membership = SimpleNamespace(
        user_id = 1,
        organization_id = 10,
        role = "owner",
    )
    membership_repository.get_by_user_and_organization.return_value = membership

    invitation_repository.get_by_org_id_and_email.return_value = None

    invitation = SimpleNamespace(
        organization_id = 10,
        invited_by = 1,# who invited i.e user_id 
        email = "test@example.com",
    )
    invitation_repository.create.return_value = invitation

    organization = SimpleNamespace( # this organization member/owner invited the email
        id = 10,
        name = "Test Organization",
    )
    organization_repository.get_by_organization_id.return_value = organization

    # actual service method called
    result = await service.create_invitation(
        organization_id=10,
        user_id=1,
        email = "test@example.com",
    )

    invitation_repository.create.assert_awaited_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(invitation)
    email_service.send_invitation_email.assert_awaited_once_with(
        email = "test@example.com",
        invitation_token = "test-token",
        organization_name = "Test Organization",
    )

    assert result is invitation


@pytest.mark.asyncio
async def test_create_invitation_non_member( # inviter is not the member of the organization
    db,
    membership_repository,
    invitation_repository,
    organization_repository,
    email_service,
    service,
):
    membership_repository.get_by_user_and_organization.return_value = None

    # actual service method called
    with pytest.raises(HTTPException) as exc_info:
        await service.create_invitation(
            organization_id=10,
            user_id=1,
            email = "test@example.com",
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Organization not found"

    membership_repository.get_by_user_and_organization.assert_awaited_once()
    invitation_repository.create.assert_not_awaited()
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()
    email_service.send_invitation_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_invitation_status_accepted(
    db,
    membership_repository,
    invitation_repository,
    organization_repository,
    email_service,
    service,
):
    membership = SimpleNamespace(
        user_id = 1,
        organization_id = 10,
        role = "owner",
    )
    membership_repository.get_by_user_and_organization.return_value = membership

    invitation = SimpleNamespace(
        organization_id = 10,
        invited_by = 1,# who invited i.e user_id 
        email = "test@example.com",
        status = "accepted",
    )
    invitation_repository.get_by_org_id_and_email.return_value = invitation

    # actual service method called
    with pytest.raises(ValueError) as exc_info:
        await service.create_invitation(
            organization_id=10,
            user_id=1,
            email = "test@example.com",
        )   

    assert str(exc_info.value) == "Invitee already member of organization"

    membership_repository.get_by_user_and_organization.assert_awaited_once()
    invitation_repository.get_by_org_id_and_email.assert_awaited_once()
    invitation_repository.create.assert_not_awaited()
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()
    email_service.send_invitation_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_invitation_status_pending(
    db,
    membership_repository,
    invitation_repository,
    organization_repository,
    email_service,
    service,
):
    membership = SimpleNamespace(
        user_id = 1,
        organization_id = 10,
        role = "owner",
    )
    membership_repository.get_by_user_and_organization.return_value = membership

    invitation = SimpleNamespace(
        organization_id = 10,
        invited_by = 1,# who invited i.e user_id 
        email = "test@example.com",
        status = "pending",
    )
    invitation_repository.get_by_org_id_and_email.return_value = invitation

    organization = SimpleNamespace( # this organization member/owner invited the email
            id = 10,
            name = "Test Organization",
        )
    organization_repository.get_by_organization_id.return_value = organization
    
    # actual service method called
    await service.create_invitation(
        organization_id=10,
        user_id=1,
        email = "test@example.com",
    )   

    membership_repository.get_by_user_and_organization.assert_awaited_once()
    invitation_repository.get_by_org_id_and_email.assert_awaited_once()
    invitation_repository.create.assert_not_awaited()
    db.commit.assert_awaited_once()
    db.flush.assert_awaited_once()
    email_service.send_invitation_email.assert_awaited_once()