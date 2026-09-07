# this file contains all the fixtures
from httpx import ASGITransport, AsyncClient
# AsyncClient - lets our test make http requests (programmatic version of swagger/postman)
# ASGITransport - allows httpx to communicate directly with fastapi app inside test
# instead of sending the request through 127.0.0.1:8000
import pytest_asyncio

from app.main import app

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.base import Base
from app.db.session import get_db
from sqlalchemy.pool import NullPool


@pytest_asyncio.fixture(scope="session", autouse=True)
async def dispose_engine():
    yield
    await test_engine.dispose()


@pytest_asyncio.fixture
async def client():# function scope

    transport = ASGITransport(app=app)

    async with AsyncClient( # opens and closes the client request
        transport=transport,
        base_url="http://test"
    ) as client:
        
        yield client



TEST_DATABASE_URL = "postgresql+asyncpg://postgres:4269@localhost:5432/saas_test_db"


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo = True,
    poolclass = NullPool,# due to this db connections are not reused from connection pool.
    # once they are made and used for a request then they are completely destroyed. Cost per request increases
    # as new connection each time.
)


TestSessionLocal = async_sessionmaker(
    bind = test_engine,
    class_= AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture # (autouse = True) automatically run this fixture for every test
async def setup_database():

    async with test_engine.begin() as connection:

        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )


async def override_get_db():

    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db # so whenever client requests needs
# fastapi overrides get_db with this function.