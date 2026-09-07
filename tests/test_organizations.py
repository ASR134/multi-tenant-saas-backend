import pytest


@pytest.mark.asyncio
async def test_create_organization(client,setup_database):

    # 1. register
    await client.post(
        "/api/v1/users",
        json = {
            "email" : "user@example.com",
            "password" : "12345",
            "full_name" : "user",
        },
    )

    # 2. login
    login_response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"user@example.com",
            "password":"12345",
        },
    )

    token = login_response.json()["access_token"]


    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name":"Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Domain"
    assert "id" in data



@pytest.mark.asyncio
async def test_get_organizations(client,setup_database):

    # 1. register
    await client.post(
            "/api/v1/users",
            json = {
                "email" : "user@example.com",
                "password" : "12345",
                "full_name" : "user",
            },
        )

    # 2. login
    login_response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"user@example.com",
            "password":"12345",
        },
    )

    token = login_response.json()["access_token"]

    # 3.create organization 
    await client.post(
            "/api/v1/organizations",
            json = {
                "name":"Domain",
            },
            headers = {
                "Authorization" : f"Bearer {token}",
            },
        )
    
    # 4. get all organizations
    response = await client.get(
        "/api/v1/organizations",
        headers = {
            "Authorization":f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json() # list
    assert len(data) == 1
    assert data[0]["name"] == "Domain"


@pytest.mark.asyncio
async def test_get_organization_by_org_id(client,setup_database):

    # 1. register
    await client.post(
            "/api/v1/users",
            json = {
                "email" : "user@example.com",
                "password" : "12345",
                "full_name" : "user",
            },
        )
    
    # 2. login
    login_response = await client.post(
            "/api/v1/auth/login",
            data = {
                "username":"user@example.com",
                "password":"12345",
            },
        )
    
    token = login_response.json()["access_token"]
    
    # 3. create organization 
    response = await client.post(
            "/api/v1/organizations",
            json = {
                "name":"Domain",
                },
            headers = {
                "Authorization" : f"Bearer {token}",
            },
        )

    org_id = response.json()["id"]

    # 4. get organization
    response = await client.get(
        f"/api/v1/organizations/{org_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Domain"
    assert data["id"] == org_id


@pytest.mark.asyncio
async def test_get_non_existent_organization(client,setup_database):

    # 1. register
    await client.post(
            "/api/v1/users",
            json = {
                "email" : "user@example.com",
                "password" : "12345",
                "full_name" : "user",
            },
        )
    
    # 2. login
    login_response = await client.post(
            "/api/v1/auth/login",
            data = {
                "username":"user@example.com",
                "password":"12345",
            },
        )
    
    token = login_response.json()["access_token"]
    
    # 3. get non existent organization
    response = await client.get(
        f"/api/v1/organizations/100000",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_access_other_users_organization(client,setup_database):

    # register user A
    await client.post(
            "/api/v1/users",
            json = {
                "email" : "userA@example.com",
                "password" : "12345",
                "full_name" : "user A",
            },
        )
    
    # login user A
    login_response = await client.post(
            "/api/v1/auth/login",
            data = {
                "username":"userA@example.com",
                "password":"12345",
            },
        )
    
    token_user_A = login_response.json()["access_token"]


    # register user B
    await client.post(
                "/api/v1/users",
                json = {
                    "email" : "userB@example.com",
                    "password" : "12345",
                    "full_name" : "user B",
                },
            )

    # login user B
    login_response = await client.post(
            "/api/v1/auth/login",
            data = {
                "username":"userB@example.com",
                "password":"12345",
            },
        )

    token_user_B = login_response.json()["access_token"]

    # create organization by user B
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name":"Domain",
            },
        headers = {
            "Authorization" : f"Bearer {token_user_B}",
        },
    )

    org_id_user_B = response.json()["id"]

    # user A tries to access org of user B
    response = await client.get(
        f"/api/v1/organizations/{org_id_user_B}",
        headers = {
            "Authorization" : f"Bearer {token_user_A}",
        },
    )

    assert response.status_code == 403