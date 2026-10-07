# this file contains all fixtures
# fixture - no calling required, scoping and caching, autouse
import os
# Pydantic BaseSettings reads configuration from multiple sources. 
# If the same setting(redis_url) exists in both the environment and .env, the environment variable takes priority.
os.environ["REDIS_URL"] = "redis://localhost:6379" # that why it is loaded before the app loads for testing.

from dotenv import load_dotenv

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
# AsyncClient - lets our test make http requests (programmatic version of swagger/postman)
# ASGITransport - allows httpx to communicate directly with fastapi app inside test
# instead of sending the request through 127.0.0.1:8000

from app.db.redis import redis_client
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from app.main import app
from app.db.session import get_db
from app.db.base import Base

from unittest.mock import AsyncMock, patch
from app.models.user import User
from sqlalchemy import select


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


test_engine = create_async_engine(
    TEST_DATABASE_URL, # type: ignore
    echo=True,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_= AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():

    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture # used to create async fixturess
async def client():# fixture scope = function by default -> 100 tests, fixture is executed 100 times.
    # creates http client

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client # pauses until fixture scope is finished


@pytest_asyncio.fixture
async def setup_database():# fixture scope = function by default
    # creates tables for test and drops them after test completion
    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )


@pytest_asyncio.fixture
async def db_session():
    # this is used when in a test we want to interact with db. Our api already gets db in fastapi 
    # which gets overridden by override_get_db().
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_redis():# for clearing the keys related to rate limits

    keys = await redis_client.keys("login:fail:*")# gives list of bytes or strings (depends on decode_responses)

    if keys:
        await redis_client.delete(*keys) # delete if any from prev tests

    yield

    keys = await redis_client.keys("login:fail:*")# delete if any from the current test which ran

    if keys:
        await redis_client.delete(*keys)


# to reduce redundancy of creating verified users and login to get access token
@pytest_asyncio.fixture
async def create_verified_user(
    client, # pytest dosen't create duplicate fixture instances it passes the same instance
    db_session, # no setup_database as tables are already created as the test was called
):
    async def _create_user(
            email,
            password,
            full_name,
    ):
        with patch(
            target="app.services.email.EmailService.send_verification_email",
            new_callable=AsyncMock,
        ) as send_mock_email:

            response = await client.post(
                "/api/v1/users",
                json = {
                    "email" : email,
                    "password" : password,
                    "full_name" : full_name,
                },
            )

        assert response.status_code == 201

        result = await db_session.execute(
            select(User).where(
                User.email == "test@example.com",
            ),
        )

        user = result.scalar_one()
        user.email_verified = True

        await db_session.commit()

        return user

    return _create_user


@pytest_asyncio.fixture
async def auth_token(
    client,
):
    async def _login(
            email,
            password,
    ):

        response = await client.post(
            "/api/v1/auth/login",
            data = {
                "username" : email,
                "password" : password,
            },
        )

        assert response.status_code == 200

        return response.json()["access_token"]

    return _login
