import pytest


# ------------------------------------------------- Testing register endpoint ("/api/v1/users")

@pytest.mark.asyncio
async def test_register_user(client,setup_database):

    response = await client.post(
        "/api/v1/users",
        json={
            "email":"test@example.com",
            "password":"password123",
            "full_name":"Test User",
        },
    )

    assert response.status_code == 201

    data = response.json()# data is a python obj -> dict

    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"



@pytest.mark.asyncio
async def test_register_duplicate_email(client,setup_database):

    user_data = {
        "email":"duplicate@example.com",
        "password":"123",
        "full_name":"First User",
    }

    response = await client.post(
        "/api/v1/users",
        json = user_data,
    )

    assert response.status_code == 201

    response = await client.post(
        "/api/v1/users",
        json = {
            "email":"duplicate@example.com",
            "password":"345",
            "full_name":"Second User",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(client,setup_database):

    response = await client.post(
        "/api/v1/users",
        json = {
            "email":"not_an_email",
            "password":"844",
            "full_name":"alex shae",
        },
    )

    assert response.status_code == 422





# ---------------------------------------------------------------Testing login endpoint("/api/v1/auth/login")

@pytest.mark.asyncio
async def test_login_user(client,setup_database):

    # 1. register the user
    await client.post(
        "/api/v1/users",
        json = {
            "email":"login@example.com",
            "password":"123",
            "full_name":"login_user",
        },
    )

    # now login

    response = await client.post(
        "/api/v1/auth/login",
        data ={
            "username":"login@example.com",
            "password":"123",
        },
    )

    assert response.status_code == 200

    data = response.json() 

    assert "access_token" in data
    assert data["token_type"] == "bearer"



@pytest.mark.asyncio
async def test_login_wrong_password(client,setup_database):

    await client.post(
        "/api/v1/users",
        json = {
            "email":"user@example.com",
            "password":"123",
            "full_name":"user",
        },
    )

    # now login with wrong password

    response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"user@example.com",
            "password":"1234",
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_non_existent_user(client,setup_database):

    response = await client.post(
            "/api/v1/auth/login",
            data = {
                "username":"non_existent@example.com",
                "password":"1234",
            }
        )
    
    assert response.status_code == 401





# -----------------------------------------------------Testing authorize endpoint("/api/v1/users/me")

@pytest.mark.asyncio
async def test_get_current_user(client,setup_database):

    # 1. register a user
    await client.post(
        "/api/v1/users",
        json={
            "email":"user@example.com",
            "password":"12345",
            "full_name":"user",
        },
    )

    # 2. login user
    login_response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"user@example.com",
            "password":"12345",
        }
    )

    token = login_response.json()["access_token"]

    # access /users/me with jwt
    # in real frontends we have to attach the token manually in every subsequent requests.
    # whereas in swagger ai testing, the swagger ui hits the login point and attaches the token in header of each subsequent request.
    respose = await client.get(
        "/api/v1/users/me",
        headers = {
            "Authorization" : f"Bearer {token}"
        },
    )

    assert respose.status_code == 200

    data = respose.json()

    assert data["email"] == "user@example.com"
    assert data["full_name"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_without_token(client,setup_database):

    response = await client.get(
        "/api/v1/users/me",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client,setup_database):

    response = await client.get(
        "/api/v1/users/me",
        headers = {
            "Authorization" : "invalid-type",
        },
    )

    assert response.status_code == 401