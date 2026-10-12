from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.services.project import ProjectService
import json
from datetime import datetime

@pytest.fixture
def db():
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