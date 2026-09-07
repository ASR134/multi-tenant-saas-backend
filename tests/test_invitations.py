import pytest


@pytest.mark.asyncio
async def test_create_invitation(client,setup_database):

    # register
    await client.post(
        "/api/v1/users",
        json = {
            "email":"user@example.com",
            "password":"12345",
            "full_name":"user",
        },
    )

    # login
    login_response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"user@example.com",
            "password":"12345",
        },
    )

    token = login_response.json()["access_token"]

    # create organization

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

    # create invitation
    response = await client.post(
        f"/api/v1/invitations/{org_id}",
        json = {
            "email":"invite@gmail.com",
        },
        headers = {
            "Authorization":f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data =response.json()

    assert data["organization_id"] == org_id
    assert "id" in data
    assert "invited_by" in data
    assert data["status"] == "pending"
    assert "token" in data
    assert data["email"] == "invite@gmail.com"


@pytest.mark.asyncio
async def test_non_member_cannot_create_invitaion(client,setup_database):

    # register user A
    await client.post(
        "/api/v1/users",
        json = {
            "email":"userA@example.com",
            "password":"12345",
            "full_name":"user",
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

    token_A = login_response.json()["access_token"]

    # create organization by A
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name":"Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token_A}",
        },
    )

    org_id_A = response.json()["id"]

    # register user b
    response = await client.post(
        "/api/v1/users",
        json = {
            "email":"userB@example.com",
            "password":"12345",
            "full_name":"userB",
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
    
    token_B = login_response.json()["access_token"]
    
    # create invitation by user B in org A
    response = await client.post(
        f"/api/v1/invitations/{org_id_A}",
        json = {
            "email":"invite@gmail.com",
        },
        headers = {
            "Authorization":f"Bearer {token_B}",
        },
    )

    assert response.status_code == 403

    data =response.json()

    assert data["detail"] == "You are not member of this organization"


@pytest.mark.asyncio
async def test_accept_invitation(client,setup_database):

    # register user A
    await client.post(
        "/api/v1/users",
        json = {
            "email":"userA@example.com",
            "password":"12345",
            "full_name":"user",
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

    token_A = login_response.json()["access_token"]

    # create organization by A
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name":"Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token_A}",
        },
    )

    org_id_A = response.json()["id"]

    # user A invites B
    response = await client.post(
            f"/api/v1/invitations/{org_id_A}",
            json = {
                "email":"userB@example.com",
            },
            headers = {
                "Authorization":f"Bearer {token_A}",
            },
        )

    invitaion_token = response.json()["token"]

    # register user b
    response = await client.post(
        "/api/v1/users",
        json = {
            "email":"userB@example.com",
            "password":"12345",
            "full_name":"userB",
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
    
    token_B = login_response.json()["access_token"]
    
    # accepts invitation
    response = await client.post(
        f"/api/v1/invitations/accept?token={invitaion_token}",
        headers = {
            "Authorization" : f"Bearer {token_B}",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_id"] == org_id_A
    assert data["status"] == "accepted"
    assert data["email"] == "userB@example.com"
    assert data["token"] == invitaion_token


@pytest.mark.asyncio
async def test_wrong_user_cannot_accept_invitation(client,setup_database):

    # register user A
    await client.post(
        "/api/v1/users",
        json = {
            "email":"userA@example.com",
            "password":"12345",
            "full_name":"user",
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

    token_A = login_response.json()["access_token"]

    # create organization by A
    response = await client.post(
        "/api/v1/organizations",
        json = {
            "name":"Domain",
        },
        headers = {
            "Authorization" : f"Bearer {token_A}",
        },
    )

    org_id_A = response.json()["id"]

    # user A invites B
    response = await client.post(
            f"/api/v1/invitations/{org_id_A}",
            json = {
                "email":"userB@example.com",
            },
            headers = {
                "Authorization":f"Bearer {token_A}",
            },
        )

    invitaion_token = response.json()["token"]

    # register user C
    response = await client.post(
        "/api/v1/users",
        json = {
            "email":"userC@example.com",
            "password":"12345",
            "full_name":"userB",
        },
    )

    # login user C
    login_response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"userC@example.com",
            "password":"12345",
        },
    )
    
    token_C = login_response.json()["access_token"]
    
    # accepts invitation
    response = await client.post(
        f"/api/v1/invitations/accept?token={invitaion_token}",
        headers = {
            "Authorization" : f"Bearer {token_C}",
        }
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_invitations(client,setup_database):

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
    login_response = await client.post(
        "/api/v1/auth/login",
        data = {
            "username":"user@example.com",
            "password":"12345",
        },
    )

    token = login_response.json()["access_token"]

    # create organization by A
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

    # user A invites B
    response = await client.post(
            f"/api/v1/invitations/{org_id}",
            json = {
                "email":"userB@example.com",
            },
            headers = {
                "Authorization":f"Bearer {token}",
            },
        )

    invitaion_token = response.json()["token"]

    # user invites C
    response = await client.post(
                f"/api/v1/invitations/{org_id}",
                json = {
                    "email":"userC@example.com",
                },
                headers = {
                    "Authorization":f"Bearer {token}",
                },
            )
    
    # get invitations
    response = await client.get(
        f"/api/v1/invitations/{org_id}",
        headers = {
            "Authorization" : f"Bearer {token}",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["organization_id"] == org_id
    assert data[1]["organization_id"] == org_id
    assert data[0]["email"] == "userB@example.com"
    assert data[1]["email"] == "userC@example.com"