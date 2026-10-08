import pytest


@pytest.mark.asyncio
async def test_create_project(
    client, # passed here coz used by test + create_verified_user + auth_token
    setup_database,# passed here only for creating tables once
    create_verified_user,
    auth_token,
):
    await create_verified_user( # passes the above client fixture instance
        "test@example.com",
        "12345678",
        "Test User",
    )

    token = await auth_token( # passes the above client fixture instance
        "test@example.com",
        "12345678",
    )

    # create organization
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Team",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    org_id = response.json()["id"]

    # create project 
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name" : "Project",
            "description" : "Desc",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["organization_id"] == org_id
    assert data["name"] == "Project"
    assert data["description"] == "Desc"




@pytest.mark.asyncio
async def test_get_projects( # by organization_id
    client,
    setup_database,
    create_verified_user,
    auth_token,
):
    await create_verified_user(
        "test@example.com",
        "12345678",
        "Test User",
    )

    token = await auth_token(
        "test@example.com",
        "12345678",
    )

    # create a organization
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Team",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    org_id = response.json()["id"]

    # create projects
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name" : "Project1",
            "description" : "Desc1",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    assert response.status_code == 201
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name" : "Project2",
            "description" : "Desc2",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    assert response.status_code == 201

    # get projects
    response = await client.get(
        f"/api/v1/projects/{org_id}",
        params = {
            "page" : 1,
            "limit" : 20,
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["organization_id"] == org_id
    assert data[0]["name"] == "Project1"
    assert data[0]["description"] == "Desc1"



@pytest.mark.asyncio
async def test_get_project( # by organization_id and user_id
    client,
    setup_database,
    create_verified_user,
    auth_token,
):
    await create_verified_user(
        "test@example.com",
        "12345678",
        "Test User",
    )

    token = await auth_token(
        "test@example.com",
        "12345678",
    )

    # create a organization
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Team",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    org_id = response.json()["id"]

    # create projects
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name" : "Project",
            "description" : "Desc",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    assert response.status_code == 201
    project_id = response.json()["id"]

    # get project by org_id and user_id
    response = await client.get(
        f"/api/v1/projects/{org_id}/{project_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_id"] == org_id
    assert data["id"] == project_id
    assert data["name"] == "Project"
    assert data["description"] == "Desc"