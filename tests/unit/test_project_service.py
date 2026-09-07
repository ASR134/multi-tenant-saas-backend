# unit tests are used to test logic without any involvement of dbms
# we will use mocking -> a fake dependency using test

import pytest
from unittest.mock import AsyncMock,MagicMock
from fastapi import HTTPException

from app.services.project import ProjectService


@pytest.mark.asyncio
async def test_create_project_non_member():

    # fake database session
    db = MagicMock() # creates a genric fake python object

    # create service
    service = ProjectService(db) # at this point membership_repository and project_repository attributes are real only db attribute is fake.

    # fake membership repo
    # AsyncMock acts as fake asynchronous function
    service.membership_repository.get_by_user_and_organization = AsyncMock(
        return_value = None
    ) # means whenever this service asks for membership pretend the repo returns None.

    with pytest.raises(HTTPException) as exc_info:
        await service.create_project( # this is real function
            organization_id=1,
            name = "Test Project",
            user_id=2,
            description="Test Description",
        ) # membership check runs inside this which is fake so returns None.

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You are not member of this organization"


@pytest.mark.asyncio
async def test_create_project_success():

    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    service = ProjectService(db)

    # pretend user is a member
    service.membership_repository.get_by_user_and_organization = AsyncMock(
        return_value = MagicMock() # creates a generic fake python object
    )

    # fake project returned by repo
    fake_project = MagicMock()
    fake_project.id = 1
    fake_project.organization_id = 1
    fake_project.name = "Test project"
    fake_project.description = "Test description"

    service.project_repository.create = AsyncMock(
        return_value = fake_project
    )

    # redis operations are also sync , so mock them
    # we don't want this unit test to contact real redis.
    import app.services.project as project_module

    project_module.redis_client.keys = AsyncMock(return_value = [])
    project_module.redis_client.delete = AsyncMock()

    result = await service.create_project(
        organization_id=1,
        name = "Test project",
        user_id =2,
        description = "Test description",
    )

    assert result == fake_project

    service.membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        user_id=2,
        organization_id=1,
    )

    service.project_repository.create.assert_awaited_once_with(
        organization_id=1,
        name="Test project",
        description="Test description",
    )

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(fake_project)



