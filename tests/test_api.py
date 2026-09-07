import pytest

from app.main import app


@pytest.mark.asyncio # plugin that gives pytest the ability to execute async test functions
async def test_unauthenticated_request(client,setup_database):# pytest recognizes functions beginning with test_

        response = await client.get(
            "/api/v1/tasks/1/1"
        )

        assert response.status_code == 401 # assert -> expecting
