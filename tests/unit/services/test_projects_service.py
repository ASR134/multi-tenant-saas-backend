from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.services.project import ProjectService
import json
from datetime import datetime

@pytest.fixture
def db(): # by default functional scope
    session = MagicMock()

    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    return session


@pytest.fixture
def project_repository():
    repo = MagicMock()

    repo.create = AsyncMock()
    repo.get_by_organization_id = AsyncMock()
    repo.get_by_org_and_project_id = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()

    return repo


@pytest.fixture
def membership_repository():
    repo = MagicMock()

    repo.get_by_user_and_organization = AsyncMock()

    return repo


@pytest.fixture
def redis_mock():
    redis = MagicMock() # mocking redis client object

    redis.keys = AsyncMock(return_value=[])
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()

    return redis


@pytest.fixture
def service(
    db,
    project_repository,
    membership_repository,
    redis_mock,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.services.project.ProjectRepository",
        lambda db : project_repository,
    )

    monkeypatch.setattr(
        "app.services.project.MembershipRepository",
        lambda db : membership_repository,
    )

    monkeypatch.setattr(
        "app.services.project.redis_client",
        redis_mock,
    )

    return ProjectService(db)

#-------------------------------------------------------------------------------------------------------
# create_project()
@pytest.mark.asyncio
async def test_create_project_success(
    db,
    project_repository,
    membership_repository,
    redis_mock,
    service,
):
    # arrange
    membership = SimpleNamespace(
        user_id=1,
        organization_id=10,
        role="owner",
    )

    project = SimpleNamespace( # only give those attributes which are being used in sevice method
        id=100,
        organization_id=10,
        name="Test Project",
        description="Test description",
    )

    membership_repository.get_by_user_and_oranization.return_value = membership

    project_repository.create.return_value = project

    # act
    result = await service.create_project(
        organization_id=10,
        name="Test Project",
        user_id=1,
        description="Test description",
    )

    # assert membership repo function
    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        user_id = 1,
        organization_id = 10,
    )
    #assert project repo function
    project_repository.create.assert_awaited_once_with(
        organization_id = 10,
        name = "Test Project",
        description = "Test description",
    )

    print("Test db:", id(db))
    print("Service db:", id(service.db))
    print("Same object:", db is service.db)
    print("Commit await count:", db.commit.await_count)
    # assert db operations
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(project)

    # assert cache invalidation
    redis_mock.keys.assert_awaited_once_with(
        "projects:org:10:page:*",
    )

    redis_mock.delete.assert_not_awaited()

    assert result is project


@pytest.mark.asyncio
async def test_create_project_non_member(
    db,
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    # arrange 
    membership_repository.get_by_user_and_organization.return_value = None

    #act
    with pytest.raises(HTTPException) as exc_info:
        await service.create_project(
            organization_id=10,
            user_id=1,
            name="Test Project",
            description="Test description",
        )

    # verify the error
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Organization not found"

    # verify project creation never happens
    project_repository.create.assert_not_awaited()

    # verify no db operations
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()

    # verify no redis cache operations
    redis_mock.keys.assert_not_awaited()
    redis_mock.delete.assert_not_awaited()


#----------------------------------------------------------------------------------------------
# get_projects_for_organization()

@pytest.mark.asyncio
async def test_get_projects_for_organization_cache_hit(
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    # arrange
    membership = SimpleNamespace(
        user_id = 1,
        oraganization_id = 10,
        role = "owner",
    )

    membership_repository.get_by_user_and_organization.return_value = membership

    cached_projects = [
        {
            "id" : 100,
            "organization_id" : 10,
            "name" : "Test Project",
            "description" : "Test description",
        }
    ]

    redis_mock.get.return_value = json.dumps(cached_projects)

    # act
    result = await service.get_projects_for_organization(
        organization_id=10,
        user_id=1,
        page=1,
        limit=10,
    )

    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        user_id=1,
        organization_id=10,
    )

    redis_mock.get.assert_awaited_once_with(
        "projects:org:10:page:1:limit:10",
    )

    project_repository.get_by_organization_id.assert_not_awaited()

    redis_mock.set.assert_not_awaited()

    assert result == cached_projects


@pytest.mark.asyncio
async def test_get_projects_for_organization_cache_miss(
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    membership = SimpleNamespace(
        organization_id = 10,
        user_id = 1,
        role = "owner",
    )

    membership_repository.get_by_user_and_organization.return_value = membership

    projects = [
        SimpleNamespace(
            organization_id = 10,
            name = "Test Project",
            description = "Test description",
            id = 100,
            created_at=datetime(2026, 10, 12, 10, 0, 0),
            version = 1,
        )
    ]

    project_repository.get_by_organization_id.return_value = projects

    #act
    result = await service.get_projects_for_organization(
        organization_id=10,
        user_id=1,
        page=1,
        limit=10,
    )

    # assert project repo call
    project_repository.get_by_organization_id.assert_awaited_once_with(
        organization_id = 10,
        page = 1,
        limit = 10,
    )

    # assert redis cache lookup
    redis_mock.get.assert_awaited_once_with(
        "projects:org:10:page:1:limit:10",
    )

    # assert redis set 
    redis_mock.set.assert_awaited_once_with(
        "projects:org:10:page:1:limit:10",
        json.dumps([
            {
                "id" : 100,
                "organization_id" : 10,
                "name" : "Test Project",
                "description" : "Test description",
                "created_at" : "2026-10-12T10:00:00", # .isoformat() converts datetime obj to iso format string
                "version" : 1,
            },
        ]),
        ex=60,
    )

    assert result == projects


@pytest.mark.asyncio
async def test_get_projects_for_organization_non_member(
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    # arrange
    membership_repository.get_by_user_and_organization.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_projects_for_organization(
            organization_id=10,
            user_id=1,
            page=1,
            limit=10,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Organization not found"

    project_repository.get_by_organization_id.assert_not_awaited()

    redis_mock.get.assert_not_awaited()
    redis_mock.set.assert_not_awaited()

#---------------------------------------------------------------------------------------------------------
# get_project_with_org_and_project_id()

@pytest.mark.asyncio
async def test_get_project_cache_hit(
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    # arrange
    membership = SimpleNamespace( # initialise only attributes that will be used in test
        organization_id = 10,
        user_id = 1,
        role = "owner"
    )

    membership_repository.get_by_user_and_organization.return_value = membership

    project = { # SimpleNamespace canno be serialised.
        "organization_id" : 10,
        "name" : "Test Project",
        "description" : "Test description",
    }

    redis_mock.get.return_value = json.dumps(project) # coz redis stores project in json form

    # act
    result = await service.get_project_with_org_and_project_id(
        organization_id=10,
        project_id=5,
        user_id=1,
    )

    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        organization_id = 10,
        user_id = 1,
    )

    project_repository.get_by_org_and_project_id.assert_not_awaited()

    redis_mock.get.assert_awaited_once_with(
        "project:org:10:id:5",
    )
    redis_mock.set.assert_not_awaited()

    assert result == project


@pytest.mark.asyncio
async def test_get_project_cache_miss(
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    membership = SimpleNamespace(
        user_id = 1,
        organization_id = 10,
        role = "owner",
    )

    membership_repository.get_by_user_and_organization.return_value = membership

    project =SimpleNamespace(
        organization_id = 10,
        name = "Test Project",
        description = "Test description",
        id = 5,
        created_at=datetime(2026, 10, 12, 10, 0, 0), # datetime coz .isoformat() needs datatime object.
        version = 1,
    )   

    project_repository.get_by_org_and_project_id.return_value = project

    result =await service.get_project_with_org_and_project_id(
        organization_id=10,
        project_id=5,
        user_id=1,
    )

    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        user_id = 1,
        organization_id = 10,
    )

    project_repository.get_by_org_and_project_id.assert_awaited_once_with(
        organization_id = 10,
        project_id = 5,
    )

    redis_mock.get.assert_awaited_once_with(
        "project:org:10:id:5",
    )

    redis_mock.set.assert_awaited_once_with(
        "project:org:10:id:5",
        json.dumps({ # match the order of dictionary pairs
            "id" : 5,
            "name" : "Test Project",
            "organization_id" : 10,
            "description" : "Test description",
            "created_at" : "2026-10-12T10:00:00", # .isoformat() converts datetime obj to iso format string
            "version" : 1,
        }),
        ex=60,
    )

    assert result == project



@pytest.mark.asyncio
async def test_get_project_not_found(
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    membership = SimpleNamespace(
            user_id = 1,
            organization_id = 10,
            role = "owner",
        )
    
    membership_repository.get_by_user_and_organization.return_value = membership

    project_repository.get_by_org_and_project_id.return_value = None

    # act
    with pytest.raises(HTTPException) as exc_info:
        await service.get_project_with_org_and_project_id(
            organization_id=10,
            project_id=5,
            user_id=1,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"

    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        user_id = 1,
        organization_id = 10,
    )
    
    project_repository.get_by_org_and_project_id.assert_awaited_once_with(
        organization_id = 10,
        project_id = 5,
    )
    
    redis_mock.get.assert_awaited_once_with(
        "project:org:10:id:5",
    )


@pytest.mark.asyncio
async def test_get_project_non_member(
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    membership_repository.get_by_user_and_organization.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_project_with_org_and_project_id(
            organization_id=10,
            project_id=5,
            user_id=1,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Organization not found"

    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        user_id = 1,
        organization_id = 10,
    )
        
    project_repository.get_by_org_and_project_id.assert_not_awaited()
        
    redis_mock.get.assert_not_awaited()
    redis_mock.set.assert_not_awaited()

#------------------------------------------------------------------------------------------
# update()
@pytest.mark.asyncio
async def test_update_project_success(
    db,
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    membership = SimpleNamespace(
        user_id = 1,
        organization_id = 10,
        role = "owner",
    )

    membership_repository.get_by_user_and_organization.return_value = membership
    
    project1 = SimpleNamespace( # the project which needs to be updated
        name = "update",
        description = "update",
        version = 1,
    )

    project2 = SimpleNamespace( # this is the return project after updating project
        name  = "Test Project",
        description = "Test description",
        organization_id = 10,
        version = 2,
    )

    project_repository.get_by_org_and_project_id.return_value = project1
    project_repository.update.return_value = project2

    result = await service.update_project( # service method called
        organization_id=10,
        user_id=1,
        expected_version=1, # this is the version that should be present in repo . then only we wil update
        project_id=5,
        name="Test Project",
        description="Test description",
    )

    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        organization_id = 10,
        user_id = 1,
    )

    project_repository.get_by_org_and_project_id.assert_awaited_once_with(
        organization_id = 10,
        project_id = 5,
    )

    project_repository.update.assert_awaited_once_with(
        project = project1,
        name = "Test Project",
        description = "Test description",
        expected_version = 1,
    )

    db.commit.assert_awaited_once()
    
    redis_mock.delete.assert_awaited_once_with(
        "project:org:10:id:5",
    )

    redis_mock.keys.assert_awaited_once_with(
        "projects:org:10:page:*",
    )

    assert result == project2


@pytest.mark.asyncio
async def test_update_project_version_conflict(
    db,
    membership_repository,
    project_repository,
    redis_mock,
    service,
):
    membership = SimpleNamespace(
        user_id = 1,
        organization_id = 10,
        role = "owner",
    )

    membership_repository.get_by_user_and_organization.return_value = membership
    
    project1 = SimpleNamespace( # the project which needs to be updated
        name = "update",
        description = "update",
        version = 1,
    )

    project_repository.get_by_org_and_project_id.return_value = project1
    project_repository.update.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        result = await service.update_project( # service method called
            organization_id=10,
            user_id=1,
            expected_version=2, # this is the version that should be present in repo . then only we wil update
            project_id=5,
            name="Test Project",
            description="Test description",
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Project was modified by another user"
    
    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        organization_id = 10,
        user_id = 1,
    )

    project_repository.get_by_org_and_project_id.assert_awaited_once_with(
        organization_id = 10,
        project_id = 5,
    )

    project_repository.update.assert_awaited_once_with(
        project = project1,
        name = "Test Project",
        description = "Test description",
        expected_version = 2,
    )

    db.commit.assert_not_awaited()
    
    redis_mock.delete.assert_not_awaited()

    redis_mock.keys.assert_not_awaited()