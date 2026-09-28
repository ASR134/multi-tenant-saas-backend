import pytest

from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from app.models.user import User


@pytest.mark.asyncio
async def test_register_user(# pytest sees the fixtures finds them and executes them
    client,
    setup_database,
):
    with patch(# temporarily mocks the fucntion
        target="app.services.email.EmailService.send_verification_email", 
        new_callable=AsyncMock,
    ) as mock_send_email:

        response = await client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "12345",
                "full_name": "Test User",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"

    mock_send_email.assert_awaited_once() # mock prevents real api call and records calls/arg

    args, kwargs = mock_send_email.call_args

    assert kwargs["email"] == "test@example.com"
    assert kwargs["verification_token"] 



@pytest.mark.asyncio
async def test_register_existing_verified_user(
    client,
    setup_database,
    db_session,
):

    with patch(
        target="app.services.email.EmailService.send_verification_email",
        new_callable=AsyncMock,
    ) as mock_send_email:

        response = await client.post(
            "/api/v1/users",
            json={
                "full_name" : "Test User",
                "email" : "test@example.com",
                "password" : "12345",
            },
        )

    assert response.status_code == 201

    # now we need to fetch the user and make its email verified
    result = await db_session.execute(# This is session B . not the session used by our app.
        select(User).where(
            User.email=="test@example.com",
        )
    )

    user = result.scalar_one()

    user.email_verified = True

    await db_session.commit()

    # now register with the same email

    response = await client.post(
        "/api/v1/users",
        json={
            "full_name" : "Test User",
            "email" : "test@example.com",
            "password" : "12345",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"] == "Email already registered"