import pytest


@pytest.mark.asyncio
async def test_create_comment(client,setup_database):

    # register user
    response = await client.post(
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

    # create comment
    response = await client.post(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        json = {
            "content" : "comment content",
        },
        headers = {
            "Authorization" : f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["content"] == "comment content"
    assert "created_at" in data
    assert data["task_id"] == task_id
    assert "user_id" in data



@pytest.mark.asyncio
async def test_get_comments(client,setup_database):

    # register user
    response = await client.post(
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

    # create 2 comments
    response = await client.post(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        json = {
            "content" : "comment content",
        },
        headers = {
            "Authorization" : f"Bearer {token}"
        }
    )

    response = await client.post(
            f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
            json = {
                "content" : "comment content 2",
            },
            headers = {
                "Authorization" : f"Bearer {token}"
            }
        )

    limit = 20
    page = 1
    response = await client.get(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        params = {
            "page" : 1,
            "limit" : 20,
        },
        headers={
            "Authorization":f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["content"] == "comment content"
    assert data[1]["content"] == "comment content 2"


@pytest.mark.asyncio
async def test_get_comment(client,setup_database):

    # register user
    response = await client.post(
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

    # create comment
    response = await client.post(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        json = {
            "content" : "comment content",
        },
        headers = {
            "Authorization" : f"Bearer {token}"
        }
    )

    comment_id = response.json()["id"]

    response = await client.get(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}/{comment_id}",
        headers={
            "Authorization":f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "comment content"
    assert data["id"] == comment_id
    assert "user_id" in data
    assert "created_at" in data



@pytest.mark.asyncio
async def test_delete_comment(client,setup_database):

    # register user
    response = await client.post(
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

    # create comment
    response = await client.post(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}",
        json = {
            "content" : "comment content",
        },
        headers = {
            "Authorization" : f"Bearer {token}"
        }
    )

    comment_id = response.json()["id"]
    # delete comment
    response = await client.delete(
        f"/api/v1/comments/{org_id}/{project_id}/{task_id}/{comment_id}",
        headers={
            "Authorization":f"Bearer {token}",
        },
    )

    assert response.status_code == 204