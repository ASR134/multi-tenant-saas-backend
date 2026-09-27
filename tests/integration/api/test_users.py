import pytest

@pytest.mark.asyncio
async def test_register_user(# pytest sees the fixtures finds them and executes them
    client,
    setup_database,
):

    response = await client.post(
        "/api/v1/users",
        json = {
            "email" : "test@example.com",
            "password" : "12345",
            "full_name" : "Test_User",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"]  == "Test_User"
    assert data["email"] == "test@example.com"