import pytest


@pytest.mark.asyncio
async def test_create_task(
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

    project_id = response.json()["id"]

    # create task in project
    response = await client.post(
        f"/api/v1/tasks/{org_id}/{project_id}",
        json = {
            "title" : "Task",
            "description" : "Desc",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_id"] == project_id
    assert data["title"] == "Task"
    assert data["description"] == "Desc"
    assert data["status"] == "todo"


@pytest.mark.asyncio
async def test_get_tasks(
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

    project_id = response.json()["id"]

    # create task in project
    response = await client.post(
        f"/api/v1/tasks/{org_id}/{project_id}",
        json = {
            "title" : "Task1",
            "description" : "Desc1",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    assert response.status_code == 201
    response = await client.post(
            f"/api/v1/tasks/{org_id}/{project_id}",
            json = {
                "title" : "Task2",
                "description" : "Desc2",
            },
            headers = {
                "Authorization" : f"Bearer {token}",
            },
        )
    assert response.status_code == 201

    # get tasks
    response = await client.get(
        f"/api/v1/tasks/{org_id}/{project_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["project_id"] == project_id
    assert data[0]["title"] == "Task1"
    assert data[0]["description"] == "Desc1"
    assert data[0]["status"] == "todo"

    assert data[1]["project_id"] == project_id
    assert data[1]["title"] == "Task2"
    assert data[1]["description"] == "Desc2"
    assert data[1]["status"] == "todo"