from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from app.services.task import TaskSerivce


@pytest.fixture
def db():

    session = MagicMock()

    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    return session


@pytest.fixture
def  task_repository():

    repo = MagicMock()

    repo.create = AsyncMock()
    repo.get_all_for_project = AsyncMock()
    repo.get_by_project_and_task_id = AsyncMock()
    repo.update = AsyncMock()

    return repo


@pytest.fixture
def membership_repository():
    repo = MagicMock()

    repo.get_by_user_and_organization = AsyncMock()

    return repo


@pytest.fixture
def project_repository():
    repo = MagicMock()

    repo.get_by_org_and_project_id = AsyncMock()

    return repo


@pytest.fixture
def service(
    db,
    task_repository,
    membership_repository,
    project_repository,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.task.TaskRepository",
        lambda db : task_repository,
    )

    monkeypatch.setattr(
        "app.services.task.MembershipRepository",
        lambda db : membership_repository,
    )

    monkeypatch.setattr(
        "app.services.task.ProjectRepository",
        lambda db : project_repository,
    )

    return TaskSerivce(db)


# ------------------------------------------------------------------------
# create_task()
@pytest.mark.asyncio
async def test_create_task_success(
    db,
    membership_repository,
    task_repository,
    project_repository,
    service,
):
    membership = SimpleNamespace(
        user_id = 1,
        organization_id = 10,
        role = "member",
    )
    membership_repository.get_by_user_and_organization.return_value = membership

    project = SimpleNamespace(
        organization_id = 10,
        name = "Test Project",
        description = "Test description",
    )
    project_repository.get_by_org_and_project_id.return_value = project

    task = SimpleNamespace(
        id = 100,
        project_id = 5,
        title = "Test Task",
        description = "Test description",
        status = "todo",
    )
    task_repository.create.return_value = task

    result = await service.create_task(
        organization_id=10,
        project_id=5,
        user_id=1,
        title="Test Task",
        description="Test description",
    )

    membership_repository.get_by_user_and_organization.assert_awaited_once_with(
        user_id = 1,
        organization_id = 10,
    )

    project_repository.get_by_org_and_project_id.assert_awaited_once_with(
        project_id = 5,
        organization_id = 10,
    )

    task_repository.create.assert_awaited_once_with(
        project_id = 5,
        title = "Test Task",
        description = "Test description",
    )

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(task)

    assert result is task
