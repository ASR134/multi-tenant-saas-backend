from fastapi import FastAPI,Depends
from sqlalchemy import text # helps us execute raw sql through sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine,get_db # importing engine we just created
from app.models.user import User
from app.db.base import Base
import app.models

from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.projects import router as projects_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.comments import router as comments_router
from app.api.v1.invitations import router as invitations_router

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message" : "multi-tenant-saas-backend is Working!"
    }

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                                  TESTING 


# use of Base.metadata.create_all

# @app.on_event("startup")
# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)



# test endpoints

# @app.get("/") 
# async def root():
#     async with engine.connect() as connection:
#         result = await connection.execute(text("SELECT 1"))
#     return {"result":result.scalar()}


# @app.get("/db-test")
# async def db_test(db: AsyncSession = Depends(get_db)):# its get_db not get_db(). fastapi dosen't calls get_db() directly. it is fastapi you manage the dependency for me.

#     result = await db.execute(text("SELECT * FROM students"))# await waits for one async operation to finish but let other tasks run in meantime

#     return {"result" : result.mappings().all()} # gives list of dictionary


# @app.get("/test-user")
# async def test_user(db: AsyncSession = Depends(get_db)):

#     user = User(
#         email = "aman@example.com",
#         password_hash ="test-password",
#         full_name = "Aman",
#     )

#     db.add(user)

#     await db.commit()

#     await db.refresh(user) # makes sqlalchemy fetch the current db state for that obj.

#     return {
#         "id" : user.id,
#         "email" : user.email,
#         "full_name" : user.full_name,
#         "created_at" : user.created_at,
#     }

# @app.get("/test-users")
# async def test_users(db: AsyncSession = Depends(get_db)):

#     result = await db.execute(select(User))

#     users = result.scalars().all() # gives list of User objects

#     return [
#         {
#             "id" : user.id,
#             "email" : user.email,
#             "full_name" : user.full_name,
#         }
#         for user in users
#     ]

# print(Base.metadata.tables.keys())

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    organizations_router,
    prefix="/api/v1",
)

app.include_router(
    projects_router,
    prefix="/api/v1",
)

app.include_router(
    tasks_router,
    prefix="/api/v1",
)

app.include_router(
    comments_router,
    prefix="/api/v1",
)

app.include_router(
    invitations_router,
    prefix="/api/v1",
)