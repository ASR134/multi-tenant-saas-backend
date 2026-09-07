import pytest

@pytest.mark.asyncio
async def test_create_task(client,setup_database):

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

    project_id = response.json()["id"]

    # create task
    response = await client.post(
        f"/api/v1/tasks/{org_id}/{project_id}",
        json={
            "title" : "t1",
            "description" : "task description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["title"] == "t1"
    assert data["description"] == "task description"
    assert "created_at" in data
    assert data["status"] == "todo"



@pytest.mark.asyncio
async def test_get_single_task(client,setup_database):

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

    project_id = response.json()["id"]

    # create task
    response = await client.post(
        f"/api/v1/tasks/{org_id}/{project_id}",
        json={
            "title" : "t1",
            "description" : "task description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    task_id = response.json()["id"]

    # get single task
    response = await client.get(
        f"/api/v1/tasks/{org_id}/{project_id}/{task_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "t1"
    assert data["description"] == "task description"
    assert data["status"] == "todo"
    assert "created_at" in data



@pytest.mark.asyncio
async def test_update_task(client,setup_database):

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

    project_id = response.json()["id"]

    # create task
    response = await client.post(
        f"/api/v1/tasks/{org_id}/{project_id}",
        json={
            "title" : "t1",
            "description" : "task description",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    task_id = response.json()["id"]
    task_version = response.json()["version"]

    # update task
    response = await client.patch(
        f"/api/v1/tasks/{org_id}/{project_id}/{task_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        }, 
        json = {
            "title" : "new title",
            "description" : "new desp",
            "status" : "new status",
            "version" : task_version
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "new title"
    assert data["description"] == "new desp"
    assert data["status"] == "new status"
    assert data["version"] == task_version+1
    assert "created_at" in data