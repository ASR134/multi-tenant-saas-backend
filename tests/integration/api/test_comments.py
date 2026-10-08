import pytest


@pytest.mark.asyncio
async def test_create_comment(
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

    task_id = response.json()["id"]

    # create comment
    response = await client.post(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        json = {
            "content" : "Content",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    assert response.status_code == 201
    data = response.json()

    assert data["task_id"] == task_id
    assert data["content"] == "Content"


@pytest.mark.asyncio
async def test_get_comments(
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

    task_id = response.json()["id"]

    # create comment
    response = await client.post(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        json = {
            "content" : "Content",
        },
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    assert response.status_code == 201

    # get comments
    response = await client.get(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["task_id"] == task_id
    assert data[0]["content"] == "Content"