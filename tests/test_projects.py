import pytest


@pytest.mark.asyncio
async def test_create_project(client,setup_database):

    # register user
    await client.post(
        "/api/v1/users",
        json = {
            "email":"user@example.com",
            "password":"12345",
            "full_name":"user",
        },
    )

    # login
    login_reponse = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "user@example.com",
            "password" : "12345",
        },
    )

    token = login_reponse.json()["access_token"]

    # create organization

    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    org_id = response.json()["id"]

    # create project
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name":"p1",
            "description":"project description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["name"] == "p1"
    assert data["description"] == "project description"
    assert "created_at" in data



@pytest.mark.asyncio
async def test_non_member_cannot_create_project(client,setup_database):

    # register user A
    await client.post(
        "/api/v1/users",
        json = {
            "email":"userA@example.com",
            "password":"12345",
            "full_name":"userA",
        },
    )

    # login user A
    login_reponse = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "userA@example.com",
            "password" : "12345",
        },
    )

    token_A = login_reponse.json()["access_token"]

    # create organization by user A

    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token_A}",
        },
    )

    org_id_A = response.json()["id"]

    # register user B
    await client.post(
        "/api/v1/users",
        json = {
            "email":"userB@example.com",
            "password":"12345",
            "full_name":"userB",
        },
    )

    # login user B

    login_reponse = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"userB@example.com",
            "password":"12345",
        },
    )

    token_B = login_reponse.json()["access_token"]

    # create project by user B in org A
    response = await client.post(
        f"/api/v1/projects/{org_id_A}",
        json = {
            "name":"p1",
            "description":"project description",
        },
        headers = {
            "Authorization" : f"Bearer {token_B}",
        },
    )

    assert response.status_code == 403

    data = response.json()



@pytest.mark.asyncio
async def test_get_projects(client,setup_database):

    # register user
    await client.post(
        "/api/v1/users",
        json = {
            "email":"user@example.com",
            "password":"12345",
            "full_name":"user",
        },
    )

    # login user 
    login_reponse = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "user@example.com",
            "password" : "12345",
        },
    )

    token = login_reponse.json()["access_token"]

    # create organization 
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    org_id = response.json()["id"]

    # create projects 2 projects
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name":"p1",
            "description":"project description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    await client.post(
        f"/api/v1/projects/{org_id}",
        json={
            "name": "p2",
            "description": "Second project",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    # get projects

    response = await client.get(
        f"/api/v1/projects/{org_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert "id" in data[0]
    assert data[0]["name"] == "p1"
    assert data[1]["name"] == "p2"



@pytest.mark.asyncio
async def test_get_project(client,setup_database):

    # register user
    await client.post(
        "/api/v1/users",
        json = {
            "email":"user@example.com",
            "password":"12345",
            "full_name":"user",
        },
    )

    # login user 
    login_reponse = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "user@example.com",
            "password" : "12345",
        },
    )

    token = login_reponse.json()["access_token"]

    # create organization 
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    org_id = response.json()["id"]

    # create projects 
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name":"p1",
            "description":"project description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    project_id = response.json()["id"]

    # get specific project

    response = await client.get(
        f"/api/v1/projects/{org_id}/{project_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id
    assert data["organization_id"] == org_id
    assert data["name"] == "p1"
    assert data["description"] == "project description"


@pytest.mark.asyncio
async def test_update_project(client,setup_database):

    # register user
    await client.post(
        "/api/v1/users",
        json = {
            "email":"user@example.com",
            "password":"12345",
            "full_name":"user",
        },
    )

    # login user 
    login_reponse = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "user@example.com",
            "password" : "12345",
        },
    )

    token = login_reponse.json()["access_token"]

    # create organization 
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    org_id = response.json()["id"]

    # create project
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name":"p1",
            "description":"project description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    project_id = response.json()["id"]
    project_version = response.json()["version"]

    # update project

    response = await client.patch(
        f"/api/v1/projects/{org_id}/{project_id}",
        json = {
            "name" : "p2",
            "description" : "project description changed",
            "version" : project_version,
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "p2"
    assert data["version"] == project_version+1
    assert data["description"] == "project description changed"



@pytest.mark.asyncio
async def test_delete_project(client,setup_database):

    # register user
    await client.post(
        "/api/v1/users",
        json = {
            "email":"user@example.com",
            "password":"12345",
            "full_name":"user",
        },
    )

    # login user 
    login_reponse = await client.post(
        "/api/v1/auth/login",
        data = {
            "username" : "user@example.com",
            "password" : "12345",
        },
    )

    token = login_reponse.json()["access_token"]

    # create organization 
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name" : "Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    org_id = response.json()["id"]

    # create projects 
    response = await client.post(
        f"/api/v1/projects/{org_id}",
        json = {
            "name":"p1",
            "description":"project description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    project_id = response.json()["id"]

    # delete project

    response = await client.delete(
        f"/api/v1/projects/{org_id}/{project_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 204