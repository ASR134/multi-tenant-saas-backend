import os
from dotenv import load_dotenv

load_dotenv()

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

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

@pytest.mark.asyncio
async def test_database_connection():

    async with test_engine.connect() as connection:
        result = await connection.execute(
            text("SELECT 1")
        )

        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_database_session():

    async with TestSessionLocal() as session:

        result = await session.execute(
            text("SELECT 1")
        )

        assert result.scalar() == 1