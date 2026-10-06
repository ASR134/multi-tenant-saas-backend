import pytest
from unittest.mock import AsyncMock,patch
from sqlalchemy import select
from app.models.user import User
from app.models.organization import Organization
from app.models.membership import Membership

@pytest.mark.asyncio
async def test_create_organization(
    client,
    setup_database,
    db_session,
):
    with patch(
        target="app.services.email.EmailService.send_verification_email",
        new_callable=AsyncMock,
    ):
        response = await client.post(
            "/api/v1/users",
            json = {
                "email" : "test@example.com",
                "password" : "12345678",
                "full_name" : "Test User"
            },
        )

    assert response.status_code == 201

    result = await db_session.execute(
        select(User).where(
            User.email == "test@example.com",
        )
    )
    user = result.scalar_one()
    user.email_verified = True

    await db_session.commit()

    # login user
    response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "test@example.com",
            "password" : "12345678",
        },
    )

    assert response.status_code == 200

    data = response.json()

    token = data["access_token"]

    # create organization

    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "test_organization",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },   
    )

    assert response.status_code == 201

    data = response.json()

    # verify organization in database
    result = await db_session.execute(
        select(Organization).where(
            Organization.name == "test_organization",
        ),
    )

    org = result.scalar_one()

    # verify creater is owner
    result = await db_session.execute(
        select(Membership).where(
            Membership.organization_id == org.id,
            Membership.user_id == user.id,
        ),
    )

    membership = result.scalar_one()

    assert membership.role == "owner"



@pytest.mark.asyncio
async def test_create_organization_without_auth(
    client,
):
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "team",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Not authenticated"



@pytest.mark.asyncio
async def test_create_organization_with_invalid_token(
    client,
):
    token = "invalid_token"

    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "team",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Could not validate credentials"