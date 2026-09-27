import pytest


@pytest.mark.asyncio # plugin that gives pytest ability to execute async test functions
async def test_root(client):# pytest sees client check in conftest.py and executes the function

    response = await client.get("/")

    assert response.status_code == 200