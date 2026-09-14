# importing sqlalchemy's asynchronous functionality 
from sqlalchemy.ext.asyncio import (
    AsyncSession, # asynchronous version of sqlalchemy's Session (a class)
    async_sessionmaker, # creates factory of sessions
    create_async_engine 
)

from app.core.config import settings

DATABASE_URL = settings.database_url
# postgresql+asyncpg://postgres:your_password@localhost:5433/saas_db
# asyncpg - use the async python driver to communicate with postgresql
# postgres - postgresql username
# localhost - connect postgresql server on the same machine where fastapi is running 
# saas_db - is the db we are connecting to

engine = create_async_engine(
    DATABASE_URL,
    echo = True, # tells sqlalchemy to pring sql statements it sends to postgresql
)

# later we will turn it off coz we don't want noisy sql logs in production

# engine - manages connection pool,created one/application
# session - created one/per HTTP request,manages transactions

SessionLocal = async_sessionmaker(
    bind = engine, # session should use sqlalchemy engine
    class_ = AsyncSession, # sessions produced by this should be AsyncSession objects
    expire_on_commit=False,# avoids MissingGreenlet on attribute access after commit
)

# give each request a db session and then automatically close when request is finished
async def get_db():
    async with SessionLocal() as session:
        yield session
# 1. Request comes in
# 2. FastAPI calls get_db()
# 3. SessionLocal() creates session
# 4. yield session  ← pauses here, session handed to endpoint
# 5. Endpoint function runs, uses session (queries, commits, etc.)
# 6. Endpoint returns (success or exception)
# 7. FastAPI resumes get_db() right after yield
# 8. async with block exits → session.close() runs
# 9. Response sent back to client