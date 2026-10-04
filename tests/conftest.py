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

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from app.main import app
from app.db.session import get_db
from app.db.base import Base



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



