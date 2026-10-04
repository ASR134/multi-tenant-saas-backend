import pytest

from unittest.mock import AsyncMock, patch
from sqlalchemy import select

from app.models.user import User

@pytest.mark.asyncio
async def test_login_user(
    client,
    setup_database,
    db_session,
):
    # register user
    with patch(
        target="app.services.email.EmailService.send_verification_email",
        new_callable=AsyncMock,
    ) as mock_send_email:

        response = await client.post(
            "/api/v1/users",
            json = {
                "email" : "test@example.com",
                "full_name" : "Test User",
                "password" : "12345678",
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
    result = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "test@example.com",
            "password" : "12345678",
        },
    )

    assert result.status_code == 200

    data = result.json()

    assert data["token_type"]  == "bearer"

    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(
    client,
    setup_database,
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
                "full_name" : "Test User",
            },
        )

    assert response.status_code == 201

    # now login (no need to make the registered user verified for this test -> check authenticate_user())
    response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "test@example.com",
            "password" : "wrong_password",
        },
    )

    assert response.status_code == 401 # unauthenticated

    data = response.json()

    assert data["detail"] == "Invalid email or password"